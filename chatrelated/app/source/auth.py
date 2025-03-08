from functools import wraps


def validate_token(func):
    @wraps(func)
    def validate():
        auth_header = request.headers.get('Authorization')