from dbconfig import db

class Chatusers(db.Model):
    username = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(200), nullable = False)

class Session(db.Model):
    __tablename__ = "sessions"
    session_id = db.Column(db.String(100), primary_key=True)
    host_username = db.Column(db.String(100), db.ForeignKey("chatusers.username"), nullable = False)

class Messages(db.Model):
    message_id = db.Column(db.Integer, primary_key = True)
    message = db.Column(db.String(500), nullable = False)
    user = db.Column(db.String(100), db.ForeignKey("chatusers.username"), nullable = False)
    host = db.Column(db.String(100), db.ForeignKey("chatusers.username"), nullable = False)
    session_id = db.Column(db.String(100), db.ForeignKey("sessions.session_id"), nullable=False)