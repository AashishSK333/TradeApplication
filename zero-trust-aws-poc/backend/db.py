import os
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')

def get_item(table_name, key):
    """Get an item from DynamoDB"""
    table = dynamodb.Table(table_name)
    
    try:
        response = table.get_item(Key=key)
        return response.get('Item')
    except ClientError as e:
        print(f"Error getting item from {table_name}: {e.response['Error']['Message']}")
        raise

def put_item(table_name, item):
    """Put an item in DynamoDB"""
    table = dynamodb.Table(table_name)
    
    try:
        table.put_item(Item=item)
        return item
    except ClientError as e:
        print(f"Error putting item in {table_name}: {e.response['Error']['Message']}")
        raise

def query_items(table_name, key_condition_expression, expression_attribute_values):
    """Query items from DynamoDB"""
    table = dynamodb.Table(table_name)
    
    try:
        response = table.query(
            KeyConditionExpression=key_condition_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        return response.get('Items', [])
    except ClientError as e:
        print(f"Error querying items from {table_name}: {e.response['Error']['Message']}")
        raise