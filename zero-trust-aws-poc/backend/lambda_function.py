import json
import os
from auth import validate_token
from db import get_item, put_item

def lambda_handler(event, context):
    try:
        # Extract token from Authorization header
        auth_header = event.get('headers', {}).get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return {
                'statusCode': 401,
                'body': json.dumps({'message': 'No token provided'})
            }
        
        token = auth_header.split(' ')[1]
        
        # Validate JWT token
        decoded_token = validate_token(token)
        if not decoded_token:
            return {
                'statusCode': 401,
                'body': json.dumps({'message': 'Invalid token'})
            }
        
        # Extract user info from token
        user_id = decoded_token['sub']
        email = decoded_token.get('email', '')
        
        # Process request based on path and method
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        
        if http_method == 'GET' and '/users/me' in path:
            user_data = get_item('Users', {'userId': user_id})
            
            if not user_data:
                # Create user record if it doesn't exist
                new_user = {
                    'userId': user_id,
                    'email': email,
                    'createdAt': context.aws_request_id,
                    'lastLogin': context.aws_request_id
                }
                
                put_item('Users', new_user)
                return {
                    'statusCode': 200,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Content-Type': 'application/json'
                    },
                    'body': json.dumps(new_user)
                }
            
            # Update last login time
            user_data['lastLogin'] = context.aws_request_id
            put_item('Users', user_data)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(user_data)
            }
        
        return {
            'statusCode': 404,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'message': 'Not found'})
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'message': 'Internal server error'})
        }