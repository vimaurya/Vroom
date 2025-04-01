from flask import render_template, redirect, url_for, session, flash
from flask import request, jsonify
from dbconfig import app, db
from models import Session, Messages, Chatusers
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from dotenv import load_dotenv
import os
import hashlib
from auth import validatePass
from flask_cors import CORS


load_dotenv()

app.secret_key = os.getenv("SECRET")

with app.app_context():
    db.create_all()

CORS(app)

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
            
            username_check = db.session.execute(db.select(Chatusers).filter_by(username=username)).scalar_one_or_none()
            
            if username_check:
                flash("User already exists..")
                return redirect(url_for("login"))
            
            new_user = Chatusers(
                username = username,
                password = password
            )
            
            print({f"success : new user, {username} joined"})
            db.session.add(new_user)
            db.session.commit()
            
            flash("Signed up. Login to proceed..")
            return redirect(url_for("login"))
        
    except Exception as e:
        print({"Error" : f"{e}"})


@app.route("/login/", methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'GET':
            return render_template("/login.html")
        
        elif request.method == 'POST':
            username = request.form['username']
            password = hash_password(request.form['password'])
            print(f'This is password : {password}')
            boolVal = validatePass(username, password)
            
            if boolVal:
                set_username(username)
                return redirect(url_for("join"))
            else:
                flash("Invalid username or password!", "error")
                
                return redirect(url_for("login"))
            
        
    except Exception as e:
        print({"Error" : f"{e}"})


@app.route('/logout/', methods=['POST'])
def logout():
    set_username()
    return redirect(url_for("login"))


@app.route("/join-session/",methods=['GET', 'POST'])
def join():
    try:
        if request.method == 'GET':
            return render_template("/joinSession.html")
        
        elif request.method == 'POST':
            session_id = request.form['session_id']
            session_password = hash_password(request.form['session_password'])
            
            session_check = db.session.execute(db.select(Session).filter_by(session_id = session_id)).scalar_one_or_none()
            
            if session_check:
                if session_check.session_password == session_password:
                    return redirect(url_for("new_session", id=session_id))
    
            flash("session id or password is incorrect...")
                
            return redirect(url_for("join"))
    
    except Exception as e:
        print(f"Error : {e}")


@app.route('/session/', methods=['GET', 'POST'])
def session_view():
    try:
        if request.method == 'GET':
            return render_template("/session.html")
        
        elif request.method == 'POST':
            session_id = request.form['session_id']
            session_password = hash_password(request.form['session_password'])
            session_check = db.session.execute(db.select(Session).filter_by(session_id = session_id)).scalar_one_or_none()
            
            if session_check:
                flash("Session already exists...")
                return redirect(url_for("session_view"))
            
            newSession = Session(
                session_id = session_id,
                host_username = session.get('username'),
                session_password = session_password
            )
            
            db.session.add(newSession)
            db.session.commit()
            
            return redirect(url_for("new_session", id=session_id))
    except Exception as e:
        print({"Error in session_view" : f"{e}"})


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
    
    db.session.execute(db.delete(Messages).where(Messages.session_id == id))
    db.session.commit()     
    
    lv_session = db.session.execute(db.select(Session).filter_by(session_id = id)).scalar_one()
    
    if session.get('username') == lv_session.host_username:
        db.session.delete(lv_session)
        db.session.commit()
    return redirect(url_for("join"))


@socketio.on("join")
def handle_join(data):
    try:
        session_id = data['session_id']
        join_room(session_id)
        print(f"User joined session {session_id}")
    except Exception as e:
        print(f"Error in handle_join: {e}")


@socketio.on("leave")
def handle_leave(data):
    try:
        session_id = data["session_id"]
        leave_room(session_id)
        emit("refresh", {}, room=session_id)  
        print(f"User left session {session_id}")
    except Exception as e:
        print(f"Error in handle_leave: {e}")


@socketio.on("message")
def handle_message(data):
    print(f"New message in session {data['session_id']}: {data['message']}")
    try:
        session_id = data['session_id']
        user = session.get('username')

        host = db.session.execute(db.select(Session).filter_by(session_id=session_id)).scalar_one()
        new_message = Messages(
            message=data['message'],
            user=user,
            host=host.host_username,
            session_id=session_id
        )
        db.session.add(new_message)
        db.session.commit()

        emit("message", {"user": user, "message": data['message']}, room=session_id)

    except Exception as e:
        print(f"Error in handle_message: {e}")


if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)    