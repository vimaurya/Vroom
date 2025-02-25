from functools import wraps
from flask import request, jsonify, g
from dbconfig import db
from models import User
import hashlib
import jwt
from datetime import datetime, timedelta
    

SECRET = "Thisisalltoomuchbullshit" 

TOKEN_BLOCKLIST = set()

def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401

        try:
            decoded_token = verify_jwt(auth_header)
            if decoded_token:
                g.user = decoded_token 
                g.username = g.user['username']
            else:
                return jsonify({"error": "Invalid token"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return func(*args, **kwargs)

    return wrapper


def generate_jwt(payload):
    exp = datetime.now() + timedelta(minutes=5)
    payload["exp"] = exp.timestamp()
    print(f"payload : {payload}")
    JWT = jwt.encode(payload, SECRET, algorithm="HS256")
    print(JWT)
    return JWT
    
    
def verify_jwt(token):
    try:
        token = token.split(" ")[1]
        
        if token in TOKEN_BLOCKLIST:
            raise jwt.ExpiredSignatureError
        
        decoded_token = jwt.decode(token, SECRET, algorithms=["HS256"])
        print(f'User : {decoded_token}')
        return decoded_token
    except Exception as e:
        print(f'Exception verifying jwt : {e}')
    
def signup(username, password):
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1]
    TOKEN_BLOCKLIST.add(token)
    
    if not db.session.get(User, username):
        password = password.encode('utf-8')
        p_object = hashlib.sha256(password)
        hash = p_object.hexdigest()
        
        new_user = User(
            username = username,
            password = hash
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return {"Success" : "user added, now login"}, 0
        except Exception as e:
            return e, 1
    else:
        return {"Error" : "user already exists"}, 1
    
    
def login(username, password):
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1]
    TOKEN_BLOCKLIST.add(token)
    
    try:
        data = db.session.get(User, username) 
        if data:
            password = password.encode('utf-8')
            p_object = hashlib.sha256(password)
            hash = p_object.hexdigest()
            
            if hash == data.password:
                jwt = generate_jwt({"username":data.username})
                return jwt, 0
        
    except:
        return {"Error" : "invalid credentials"}, 1