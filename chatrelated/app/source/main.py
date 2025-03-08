from flask import render_template, redirect, url_for, session
from flask import request, jsonify
from dbconfig import app, db
from models import Session, Messages
from flask_socketio import SocketIO, send



app.secret_key = "idkwtfimdt"

with app.app_context():
    db.create_all()


socketio = SocketIO(app, cors_allowed_origins="*")

def set_username(username = None):
    session['username'] = username
    session.modified = True


@app.route("/")
def home():
    return render_template("/index.html")

@app.route("/login/",methods=['POST'])
def join():
    session_id = request.form['session_id']
    set_username(request.form['username'])
    
    return redirect(url_for("new_session", id=session_id))


@app.route('/session/', methods=['GET', 'POST'])
def session_view():
    flag = request.args.get('flag')
    if request.method == 'GET':
        return render_template("/session.html", flag = flag)
    
    elif request.method == 'POST':
        set_username(request.form["username"])
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


@app.route('/session/<string:id>', methods=['GET'])
def new_session(id):
    messages = Messages.query.filter_by(session_id=id).all()
    
    msg_list = []
    
    for msg in messages:
        new_msg = {}
        new_msg['user'] = msg.user
        new_msg['message'] = msg.message
        
        msg_list.append(new_msg)
    
    return render_template("/sessionChat.html", session_id = id, messages = messages, username = session.get("username"))
    
    
@socketio.on("message")
def handle_message(data):
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
    


if __name__ == "__main__":
    app.run(debug=True)