from functools import wraps
from flask import request
from models import Chatusers
from dbconfig import db, app





def validatePass(username, password):
    user_password = db.session.execute(db.select(Chatusers).filter_by(username = username)).scalar_one_or_none()
    if user_password:
        if user_password.password == password:
            return True
    return False