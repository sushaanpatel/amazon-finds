from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
import mysql.connector
from datetime import datetime
from models import app, db2, con, Users

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
  return Users.query.get(user_id)

@login_manager.unauthorized_handler
def unauth():
    return redirect('/admin')

global paserr
paserr = ""
global proderr
proderr = ""
global product_list
product_list = []
global current_page
current_page = ""
global fromadminsearch
fromadminsearch = False

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/admin')

@app.route('/clearfilter')
def clear():
    global current_page
    global fromadminsearch
    global product_list
    product_list = []
    if current_page == '/products':
        fromadminsearch = False
        return redirect('/products')

@app.route('/delete/<int:prod_id>')
def delete(prod_id):
    con.reconnect()
    db = con.cursor()
    db.execute(f"DELETE FROM products WHERE product_id = {prod_id}")
    con.commit()
    return redirect('/products')

@app.route('/')
def index():
    global paserr
    paserr = ""
    global proderr
    proderr = ""
    global product_list
    product_list = []
    return render_template('index.html')

@app.route('/admin', methods = ["POST", "GET"])
def admin():
    global paserr
    global proderr
    proderr = ""
    global product_list
    product_list = []
    if request.method == "POST":
        password = request.form['password']
        passfromdb = Users.query.filter_by(password = "1234").first()
        if password == passfromdb.password:
            login_user(passfromdb)
            return redirect('/products')
        else:
            paserr = "Wrong Password"   
            return redirect('/admin')
    else:
        return render_template('pass-protect.html', err = paserr)

@app.route('/adminsearch', methods=["POST", "GET"])
def adminsearch():
    global product_list
    product_list = []
    global fromadminsearch
    global current_page
    current_page = '/products'
    if request.method == "POST":
        search = request.form['adsearch']
        con.reconnect()
        db = con.cursor()
        db.execute(f"SELECT * FROM products WHERE name LIKE '%{search}%'")
        query = db.fetchall()
        fromadminsearch = True
        product_list = query
        return redirect('/products')


@app.route('/products', methods = ["POST", "GET"])
@login_required
def add():
    global proderr
    global paserr
    paserr = ""
    global product_list
    global current_page
    current_page = '/products'
    if request.method == "POST":
        title = request.form['product-name']
        descrip = request.form['product-description']
        price = request.form['product-price']
        image = request.files['product-image']
        creator = request.form['product-creator']
        employ_name = request.form['employ-name']
        date = datetime.now()
        if title != "" and descrip != "" and price != "" and image != "" and creator != "" and employ_name != "":
            con.reconnect()
            db = con.cursor()
            db.execute(f"""INSERT INTO products(name, description, price, image, creator, employ_name, date, times_clicked) VALUES("{title}", "{descrip}", "{price}", "{image.filename}", "{creator}", "{employ_name}", "{date.date()}", 0)""")
            con.commit()
            return redirect('/products')
        else:
            proderr = "Please fill out all the details"
            return redirect('/products')
    else:
        if fromadminsearch:
            return render_template('products.html', products = product_list, err = proderr)
        else:
            con.reconnect()
            db = con.cursor()
            db.execute("SELECT * from products")
            product_list = db.fetchall()
            return render_template('products.html', products = product_list, err = proderr)

if __name__ == "__main__":
    app.run(debug=True)

# x = Users(password = "1234")
# db2.session.add(x)
# db2.session.commit()