from dbconfig import db

class User(db.Model):
    username = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(500), nullable=False)
    
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(100), nullable=False)
    definition = db.Column(db.String(500), nullable=True)
    deadline = db.Column(db.DateTime, nullable = True)
    is_completed = db.Column(db.Boolean, nullable = False, default = False)
    username = db.Column(db.String(50), db.ForeignKey("user.username"), nullable=False)
    