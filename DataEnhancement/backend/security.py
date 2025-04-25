import os
import jwt
import time
import logging
from functools import wraps
from flask import request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
JWT_SECRET = os.getenv('JWT_SECRET', 'fallback_secret_change_me_in_production')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
TOKEN_EXPIRATION = 3600  # 1 hour in seconds
REFRESH_THRESHOLD = 300  # 5 minutes before expiration

VALID_USERS = {
    "admin@leadgen.com": "caprae@123",
    "analyst@leadgen.com": "leadgen@456"
}

logger = logging.getLogger(__name__)

def generate_token(email):
    payload = {
        "email": email,
        "exp": time.time() + TOKEN_EXPIRATION,
        "iat": time.time()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token

def validate_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get('email')
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
        return None
    except jwt.InvalidTokenError:
        logger.error("Invalid token")
        return None

def verify_token(token):
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        current_time = time.time()
        
        if decoded['exp'] < current_time:
            return None
            
        # Check if token needs refresh (within 5 minutes of expiration)
        if decoded['exp'] - current_time < REFRESH_THRESHOLD:
            new_token = generate_token(decoded['email'])
            return {'decoded': decoded, 'new_token': new_token}
            
        return {'decoded': decoded}
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({"error": "Authorization header missing or invalid"}), 401
            
        result = validate_token(token.split(" ")[1])
        if not result:
            return jsonify({"error": "Invalid or expired token"}), 401
            
        # Add refreshed token to response if available
        response = f(*args, **kwargs)
        if isinstance(response, tuple):
            response_data, status_code = response
        else:
            response_data, status_code = response, 200
            
        if 'new_token' in result:
            if isinstance(response_data, dict):
                response_data['new_token'] = result['new_token']
            else:
                response_data = {'data': response_data, 'new_token': result['new_token']}
                
        return jsonify(response_data), status_code
            
    return decorated