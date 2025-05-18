from dbconfig import db

class URL(db.Model):
    shorturl = db.Column(db.String(50), primary_key = True)
    orgurl = db.Column(db.String(50), nullable = False)