from functools import wraps
from flask import request

def validate_token(func):
    @wraps(func)
    def validate():
        auth_header = request.headers.get('Authorization')
        
        
        
    