import os
import dotenv
import mysql.connector
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# dotenv.load_dotenv()
# db_pass = os.environ.get('DB_PASS')
# db_user = os.environ.get('DB_USER')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://b3a2577f9a4db8:642bf839@us-cdbr-east-04.cleardb.com/heroku_4ae77d286130396'
app.config['SQLALCHEMY_POOL_RECYCLE'] = 60
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/'
app.secret_key = "amazonfindsretkey"
db2 = SQLAlchemy(app)
con = mysql.connector.connect(
    host = "us-cdbr-east-04.cleardb.com",
    user = "b3a2577f9a4db8",
    password = "642bf839",
    database = "heroku_4ae77d286130396"
)

class Users(db2.Model, UserMixin):
    id = db2.Column(db2.Integer, primary_key = True)
    password = db2.Column(db2.String(50))
