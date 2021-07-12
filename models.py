import mysql.connector
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/amazonfinds'
app.config['SQLALCHEMY_POOL_RECYCLE'] = 60
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/'
app.secret_key = "amazonfindsretkey"
db2 = SQLAlchemy(app)
con = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "password",
    database = "amazonfinds"
)

class Users(db2.Model, UserMixin):
    id = db2.Column(db2.Integer, primary_key = True)
    password = db2.Column(db2.String(50))
