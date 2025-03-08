from dbconfig import db

class Session(db.Model):
    __tablename__ = "sessions"
    session_id = db.Column(db.String(100), primary_key=True)
    host_username = db.Column(db.String(50), nullable = False)

class Messages(db.Model):
    message_id = db.Column(db.Integer, primary_key = True)
    message = db.Column(db.String(500), nullable = False)
    user = db.Column(db.String(100), nullable = False)
    host = db.Column(db.String(50), nullable = False)
    session_id = db.Column(db.String(100), db.ForeignKey("sessions.session_id"), nullable=False)