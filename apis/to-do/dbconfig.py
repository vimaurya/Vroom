from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)

app.json.sort_keys = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:vikash@localhost/todo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
