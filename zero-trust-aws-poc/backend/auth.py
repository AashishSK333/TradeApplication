import json
import os
import urllib.request
import time
import jwt
from jwt.algorithms import RSAAlgorithm

# Cache for the JWKs
jwks_cache = {
    'keys': None,
    'timestamp': 0
}

def get_jwks():
    """Fetch and cache JWKs from Cognito"""
    now = time.time()
    cache_ttl = 3600  # 1 hour
    
    if jwks_cache['keys'] and (now - jwks_cache['timestamp']) < cache_ttl:
        return jwks_cache['keys']
    
    region = os.environ['AWS_REGION']
    user_pool_id = os.environ['USER_POOL_ID']
    
    url = f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'
    
    with urllib.request.urlopen(url) as response:
        jwks = json.loads(response.read())
        jwks_cache['keys'] = jwks['keys']
        jwks_cache['timestamp'] = now
        return jwks_cache['keys']

def find_jwk(kid):
    """Find the JWK for the given Key ID"""
    keys = get_jwks()
    for key in keys:
        if key['kid'] == kid:
            return key
    return None

def validate_token(token):
    """Validate the JWT token from Cognito"""
    try:
        # Decode token header without verification to get the kid
        headers = jwt.get_unverified_header(token)
        kid = headers['kid']
        
        # Get the JWK for this kid
        jwk = find_jwk(kid)
        if not jwk:
            print("No matching JWK found")
            return None
        
        # Convert JWK to PEM format
        public_key = RSAAlgorithm.from_jwk(json.dumps(jwk))
        
        # Verify the token
        region = os.environ['AWS_REGION']
        user_pool_id = os.environ['USER_POOL_ID']
        issuer = f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}'
        
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            options={'verify_exp': True},
            audience=os.environ['CLIENT_ID'],
            issuer=issuer
        )
        
        return decoded
        
    except Exception as e:
        print(f"Token validation error: {str(e)}")
        return None