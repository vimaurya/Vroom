from flask import render_template, redirect, url_for, session
from flask import request, jsonify
from dbconfig import app, db
from models import Session, Messages, Chatusers
from flask_socketio import SocketIO, send, emit
from dotenv import load_dotenv
import os
import hashlib


load_dotenv()

app.secret_key = os.getenv("SECRET")

with app.app_context():
    db.create_all()


socketio = SocketIO(app, cors_allowed_origins="*")

def set_username(username = None):
    session['username'] = username
    session.modified = True
    print(f"This is username : ", username)
    return username

def hash_password(password):
    password = password.encode('utf-8')
    p_object = hashlib.sha256(password)
    p_hash = p_object.hexdigest()
    
    return p_hash


@app.route("/", methods=['GET', 'POST'])
def signup():
    try:
        if request.method == 'GET':
            return render_template("/signup.html")

        elif request.method == 'POST':
            username = set_username(request.form['username'])
            password = hash_password(request.form['password'])
            
            new_user = Chatusers(
                username = username,
                password = password
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            return redirect(url_for("home"))
        
    except Exception as e:
        print({"Error" : f"{e}"})


@app.route("/login/", methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'GET':
            return render_template("/login.html")
        
    except Exception as e:
        print({"Error" : f"{e}"})


@app.route("/join/")
def home():
    return render_template("/index.html")


@app.route("/join-session/",methods=['POST'])
def join():
    session_id = request.form['session_id']
    
    return redirect(url_for("new_session", id=session_id))


@app.route('/session/', methods=['GET', 'POST'])
def session_view():
    try:
        flag = request.args.get('flag')
        if request.method == 'GET':
            return render_template("/session.html", flag = flag)
        
        elif request.method == 'POST':
            session_id = request.form['session_id']
            session_check = db.session.execute(db.select(Session).filter_by(session_id = session_id)).scalar_one_or_none()
            
            if session_check:
                return redirect(url_for("session_view", flag=True))
            
            newSession = Session(
                session_id = session_id,
                host_username = session.get('username')
            )
            
            db.session.add(newSession)
            db.session.commit()
            
            return redirect(url_for("new_session", id=session_id))
    except Exception as e:
        print({"Error" : f"{e}"})

@app.route('/session/<string:id>/', methods=['GET'])
def new_session(id):
    try:
        messages = Messages.query.filter_by(session_id=id).all()
        
        msg_list = []
        
        for msg in messages:
            new_msg = {}
            new_msg['user'] = msg.user
            new_msg['message'] = msg.message
            
            msg_list.append(new_msg)
        
        return render_template("/sessionChat.html", session_id = id, messages = messages, username = session.get("username"))
    except Exception as e:
        print({"error" : f"{e}"})
        
@app.route('/leave/<string:id>', methods=['GET'])
def leave_session(id):
        
    return redirect(url_for("home"))
    
    
    
@socketio.on("leave")
def leave_socket(data):
    messages = Messages.query.filter_by(user = session.get('username')).all()
    
    for message in messages:
        db.session.delete(message)

    db.session.commit()
    
    lv_session = db.session.execute(db.select(Session).filter_by(session_id = data['session_id'])).scalar_one()
    
    if session.get('username') == lv_session.host_username:
        db.session.delete(lv_session)
        db.session.commit()
        
    emit("refresh", {}, broadcast=True)   
        
    
@socketio.on("message")
def handle_message(data):
    try:
        host = db.session.execute(db.select(Session).filter_by(session_id = data['session_id'])).scalar_one()
        user = session.get('username')
        new_message = Messages(
            message = data['message'],
            user = user,
            host = host.host_username,
            session_id = data['session_id']
        )
        db.session.add(new_message)
        db.session.commit()
        
        send({"user": user, "message": data['message']}, broadcast=True)
    except Exception as e:
        print({"Error" : f"{e}"})
        


if __name__ == "__main__":
    app.run(debug=True)