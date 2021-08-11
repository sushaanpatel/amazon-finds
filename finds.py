import os
import webbrowser
import mysql.connector
from datetime import datetime
from models import app, db2, con, Users
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from scrapper import getall, updatedb
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user

# def getall(asin):
#     return {
#         "name":"NA",
#         "price":"NA",
#         "image":"NA",
#         "rating":"NA",
#         "ratingno":"NA",
#         "availability":"NA"
#         }

# def getprice(asin):
#     return "NA"

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
  return Users.query.get(user_id)

@login_manager.unauthorized_handler
def unauth():
    return redirect('/admin')

db = con.cursor()
db.execute("SELECT * FROM products")
x = db.fetchall()
for i in x:
    y = updatedb(i[1])
    rate = round(float(y['rating']))
    if y['price'] != '':
        db.execute(f"""UPDATE products SET price = '{y['price']}', availability = "{y['availability']}", rating = '{rate}' WHERE product_id = {i[0]}""")
    else:
        db.execute(f"""UPDATE products SET availability = "{y['availability']}", rating = '{rate}' WHERE product_id = {i[0]}""")
    con.commit()

global paserr
paserr = ""
global proderr
proderr = ""
global uperr
uperr = ""
global product_list
product_list = []
global display_list
display_list = []
global current_page
current_page = ""
global fromadminsearch
fromadminsearch = False
global fromsearch
fromsearch = False

def format(unformat):
    lenght = len(unformat)
    count = 0
    formated_list = []
    while count < lenght:
        try:
            temp = []
            temp.append(unformat[count])
            temp.append(unformat[count+1])
            temp.append(unformat[count+2])
            formated_list.append(temp)
            count += 3
        except IndexError:
            if lenght%3 == 1:
                x = unformat[::-1]
                y = []
                y.append(x[0])
                formated_list.append(y)
                count += 3
            if lenght%3 == 2:
                x = unformat[::-1]
                y = []
                y.append(x[0])
                y.append(x[1])
                formated_list.append(y[::-1])
                count += 3
    return formated_list

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/admin')

@app.route('/clearfilter')
def clear():
    global current_page
    global fromadminsearch
    global fromsearch
    global product_list
    product_list = []
    if current_page == '/products':
        fromadminsearch = False
        return redirect('/products')
    if current_page == '/':
        fromsearch = False
        return redirect('/')

@app.route('/buynow/<int:id>')
def buynow(id):
    global current_page
    con.reconnect()
    db = con.cursor()
    db.execute(f"SELECT times_clicked FROM products WHERE product_id = {id}")
    x = db.fetchall()[0][0]
    x += 1
    db.execute(f"""UPDATE products SET times_clicked = {x} WHERE product_id = {id} """)
    con.commit()
    db.execute(f"SELECT link FROM products WHERE product_id = {id} ")
    link = db.fetchall()
    webbrowser.open_new_tab(f'{link[0][0]}')
    if current_page == '/':
        return redirect('/')
    if current_page == '/productpage':
        return "",204

@app.route('/', methods = ["POST", "GET"])
def index():
    global paserr
    paserr = ""
    global proderr
    proderr = ""
    global product_list
    global display_list
    global current_page
    current_page = '/'
    con.reconnect()
    db = con.cursor()
    if fromsearch == False:
        display_list = []
        db.execute("SELECT * from products")
        product_list = db.fetchall()
        out = format(product_list)
        for i in out:
            display_list.append(i)
    return render_template('index.html', display = display_list, prod = product_list)

@app.route('/product/id=<int:id>', methods = ["POST", "GET"])
def product_page(id):
    global current_page
    current_page = '/productpage'
    con.reconnect()
    db = con.cursor()
    db.execute(f"""SELECT * FROM products WHERE product_id = "{id}" """)
    product = db.fetchall()
    return render_template('product-page.html', p = product[0])

@app.route('/search', methods = ["POST", "GET"])
def search():
    global display_list
    global fromsearch
    global current_page
    current_page = '/'
    if request.method == "POST":
        display_list = []
        searchword = request.form['search_bar'].lower()
        cata = request.form.get('filter')
        sub_cata = request.form.get('sub_fil')
        con.reconnect()
        db = con.cursor()
        if cata == "all":
            db.execute(f"SELECT * FROM products WHERE name LIKE '%{searchword}%'")
            query = db.fetchall()
            fromsearch = True
            out = format(query)
            for i in out:
                display_list.append(i)
        else:
            if searchword != '':
                db.execute(f"""SELECT * FROM products WHERE catagory = "{sub_cata}" and name LIKE "%{searchword}%" """)
            else:
                db.execute(f"""SELECT * FROM products WHERE catagory = "{sub_cata}" """)
            query = db.fetchall()
            fromsearch = True
            out = format(query)
            for i in out:
                display_list.append(i)
        return redirect('/')

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
        product_list = product_list[::-1]
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
        asin = request.form['asin'].upper()
        try:
            product = getall(asin)
        except:
            proderr = "Product Not Found"
            return redirect('/products')
        title = product['name'].replace('"', "'")
        price = product['price']
        rating = round(float(product['rating']))
        avail = product['availability']
        image = str(product['image'])
        descrip = str(product['descrip']).replace('"', "'")
        link = request.form['amazon-link']
        catagory = request.form.get('product-cata')
        creator = request.form['product-creator']
        employ_name = request.form['employ-name']
        date = datetime.now()
        if price == '':
            flash('1')
            price = "NA"
        if asin != "" and link != "" and creator != "" and employ_name != "" and catagory != "none":
            con.reconnect()
            db = con.cursor()
            db.execute(f"""INSERT INTO products(asin, name, description, catagory, link, image, creator, employ_name, date, times_clicked, price, rating, availability) VALUES("{asin}", "{title}", "{descrip}", "{catagory}", "{link}", "{image}", "{creator}", "{employ_name}", "{date.date()}", 0, "{price}", "{rating}", "{avail}")""")
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
            product_list = product_list[::-1]
            return render_template('products.html', products = product_list, err = proderr)

@app.route('/delete/<int:prod_id>')
def delete(prod_id):
    con.reconnect()
    db = con.cursor()
    db.execute(f"DELETE FROM products WHERE product_id = {prod_id}")
    con.commit()
    return redirect('/products')

@app.route('/updateprice/<int:id>', methods = ["POST", "GET"])
def updateprice(id):
    db = con.cursor()
    if request.method == "POST":
        price = "₹" + request.form['price']
        db.execute(f"UPDATE products SET price = '{price}' WHERE product_id = {id}")
        con.commit()
        return redirect('/products')
    else:
        db.execute(f"SELECT * FROM products WHERE product_id = {id}")
        p = db.fetchall()[0]
        return render_template("addprice.html", p = p)

@app.route('/update/<int:prod_id>', methods = ["POST", "GET"])
def update(prod_id):
    global uperr
    if request.method == "POST":
        asin = request.form['asin'].upper()
        try:
            product = getall(asin)
        except:
            uperr = "Product Not Found"
            return redirect(f'/update/{prod_id}')
        title = product['name'].replace('"', "'")
        price = product['price']
        rating = round(float(product['rating']))
        avail = product['availability']
        image = str(product['image'])
        descrip = str(product['descrip']).replace('"', "'")
        link = request.form['amazon-link']
        catagory = request.form.get('product-cata')
        creator = request.form['product-creator']
        employ_name = request.form['employ-name']
        date = datetime.now()
        if asin != "" and link != "" and creator != "" and employ_name != "" and catagory != "none":
            con.reconnect()
            db = con.cursor()
            if price == '':
                db.execute(f"""UPDATE products SET asin = "{asin}", name = "{title}", description = "{descrip}", catagory = "{catagory}", link = "{link}", image = "{image}", creator = "{creator}", employ_name = "{employ_name}", date = "{date.date()}", availability = "{avail}", rating = {rating} WHERE product_id = "{prod_id}" """)
            else:
                db.execute(f"""UPDATE products SET asin = "{asin}", name = "{title}", description = "{descrip}", catagory = "{catagory}", link = "{link}", image = "{image}", creator = "{creator}", employ_name = "{employ_name}", date = "{date.date()}", price = "{price}", availability = "{avail}", rating = {rating} WHERE product_id = "{prod_id}" """)
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

# db = con.cursor()
