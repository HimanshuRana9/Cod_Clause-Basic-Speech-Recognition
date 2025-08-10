from functools import wraps
from flask import request, jsonify
import os

API_TOKEN = os.getenv('API_TOKEN','')

def require_api_key(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('X-API-KEY') or request.args.get('token')
        if API_TOKEN and token == API_TOKEN:
            return f(*args, **kwargs)
        if not API_TOKEN:
            return f(*args, **kwargs)
        return jsonify({'error':'unauthorized'}), 401
    return wrapper
