import os
import mysql.connector
from datetime import datetime
from models import app, db2, con, Users
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from scrapper import getall, getprice, getrating, getavail
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user

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
global uperr
uperr = ""
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
        # product_id, asin, name, description, catagory, link, image, creator, employ_name, date, times_clicked
        asin = request.form['asin'].upper()
        product = getall(asin)
        title = product['name']
        image = product['image']
        descrip = request.form['product-description']
        link = request.form['amazon-link']
        catagory = request.form.get('product-cata')
        creator = request.form['product-creator']
        employ_name = request.form['employ-name']
        date = datetime.now()
        if descrip != "" and link != "" and creator != "" and employ_name != "" and catagory != "-- Select Product Catagory --":
            con.reconnect()
            db = con.cursor()
            db.execute(f"""INSERT INTO products(asin, name, description, catagory, link, image, creator, employ_name, date, times_clicked) VALUES("{asin}", "{title}", "{descrip}", "{catagory}", "{link}", "{image}", "{creator}", "{employ_name}", "{date.date()}", 0)""")
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

@app.route('/delete/<int:prod_id>')
def delete(prod_id):
    con.reconnect()
    db = con.cursor()
    db.execute(f"DELETE FROM products WHERE product_id = {prod_id}")
    con.commit()
    return redirect('/products')

@app.route('/update/<int:prod_id>', methods = ["POST", "GET"])
def update(prod_id):
    global uperr
    if request.method == "POST":
        asin = request.form['asin'].upper()
        product = getall(asin)
        title = product['name']
        image = product['image']
        descrip = request.form['product-description']
        link = request.form['amazon-link']
        catagory = request.form.get('product-cata')
        creator = request.form['product-creator']
        employ_name = request.form['employ-name']
        date = datetime.now()
        if asin != "" and descrip != "" and link != "" and creator != "" and employ_name != "" and catagory != "-- Select Product Catagory --":
            con.reconnect()
            db = con.cursor()
            db.execute(f"""UPDATE products SET asin = "{asin}", name = "{title}", description = "{descrip}", catagory = "{catagory}", link = "{link}", image = "{image}", creator = "{creator}", employ_name = "{employ_name}", date = "{date.date()}" WHERE product_id = "{prod_id}" """)
            con.commit()
            return redirect('/products')
        else:
            uperr = "Please fill out all the details"
            return redirect(f'/update/{prod_id}')
    else:
        con.reconnect()
        db = con.cursor()
        db.execute(f"SELECT * FROM products WHERE product_id = {prod_id}")
        product = db.fetchall()[0]
        return render_template('update.html', p = product, err = uperr)

if __name__ == "__main__":
    app.run(debug=True)

# x = Users(password = "1234")
# db2.session.add(x)
# db2.session.commit()