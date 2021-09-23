import os
import webbrowser
import mysql.connector
from datetime import datetime
from models import app, db2, con, Users
from flask_sqlalchemy import SQLAlchemy
from scrapper import getall, updatedb
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
  return Users.query.get(user_id)

@login_manager.unauthorized_handler
def unauth():
    return redirect('/admin')

@app.before_first_request
def before():
    session.clear()
    session['paserr'] = ""
    session['proderr'] = ""
    session['uperr'] = ""
    session['products'] = []
    session['display'] = []
    session['currentp'] = ""
    session['frmadmsearch'] = False
    session['frmsearch'] = False

def format(unformat):
    lenght = len(unformat)
    count = 0
    formated_list = []
    if unformat == []:
        formated_list = []
    else:
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
    if session['currentp'] == '/products':
        session['frmadmsearch'] = False
        return redirect('/products')
    if session['currentp'] == '/':
        session['frmsearch'] = False
        return redirect('/')

@app.route('/buynow/<int:id>')
def buynow(id):
    con.reconnect()
    db = con.cursor()
    db.execute(f"SELECT * FROM products WHERE product_id = {id}")
    x = db.fetchall()[0]
    y = x[13] + 1
    db.execute(f"""UPDATE products SET times_clicked = {y} WHERE product_id = {id} """)
    con.commit()
    return redirect(f'{x[6]}')

@app.route('/home', methods = ["POST", "GET"])
def home():
    session['frmadmsearch'] = False
    session['frmsearch'] = False
    session['currentp'] = '/'
    return redirect('/')

@app.route('/', methods = ["POST", "GET"])
def index():
    session['paserr'] = ""
    session['proderr'] = ""
    session['currentp'] = '/'
    con.reconnect()
    db = con.cursor()
    if session['frmsearch'] == False:
        db.execute("SELECT * from products")
        prod_list = db.fetchall()
        out = format(prod_list)
        for i in range(len(out)):
            out[i] = out[i][::-1]
        session['display'] = out[::-1]
    return render_template('index.html', display = session['display'])

@app.route('/product/id=<int:id>', methods = ["POST", "GET"])
def product_page(id):
    session['currentp'] = '/productpage'
    con.reconnect()
    db = con.cursor()
    db.execute(f"""SELECT * FROM products WHERE product_id = "{id}" """)
    product = db.fetchall()
    return render_template('product-page.html', p = product[0])

@app.route('/search', methods = ["POST", "GET"])
def search():
    session['currentp'] = '/'
    if request.method == "POST":
        searchword = request.form['search_bar'].lower()
        con.reconnect()
        db = con.cursor()
        db.execute(f"SELECT * FROM products WHERE name LIKE '%{searchword}%'")
        query = db.fetchall()
        session['frmsearch'] = True
        out = format(query)
        for i in range(len(out)):
            out[i] = out[i][::-1]
        session['display'] = out[::-1]
        return redirect('/')

@app.route('/filter', methods = ["POST", "GET"])
def filter():
    if request.method == "POST":
        query = session['display']
        out = []
        sub_fil = request.form['sub_fil']
        fil = request.form['filter']
        if fil == 'category':
            for j in query:
                for i in j:
                    if i[5] == sub_fil:
                        out.append(i)
        elif fil == 'price':
            if sub_fil == 'high':
                pass
            elif sub_fil == 'low':
                pass
        session['frmsearch'] = True
        temp = format(out)
        session['display'] = temp
        return redirect('/')

    
@app.route('/admin', methods = ["POST", "GET"])
def admin():
    session['proderr'] = ""
    if request.method == "POST":
        password = request.form['password']
        passfromdb = Users.query.filter_by(id = "5").first()
        if password == passfromdb.password:
            login_user(passfromdb)
            return redirect('/products')
        else:
            session['paserr'] = "Wrong Password"   
            return redirect('/admin')
    else:
        return render_template('pass-protect.html', err = session['paserr'])

@app.route('/adminsearch', methods=["POST", "GET"])
def adminsearch():
    session['currentp'] = '/products'
    if request.method == "POST":
        search = request.form['adsearch']
        con.reconnect()
        db = con.cursor()
        db.execute(f"SELECT * FROM products WHERE name LIKE '%{search}%'")
        query = db.fetchall()
        session['frmadmsearch'] = True
        session['products'] = query[::-1]
        return redirect('/products')

@app.route('/updatedb')
@app.route('/updatedb/<int:id>')
def updb(id):
    con.reconnect()
    db = con.cursor()
    db.execute("SELECT * FROM products")
    x = db.fetchall()
    for i in x:
        y = updatedb(i[1])
        rate = round(float(y['rating']))
        if y['price'] != '':
            con.reconnect()
            db.execute(f"""UPDATE products SET price = '₹{y['price']}', availability = "{y['availability']}", rating = '{rate}' WHERE product_id = {i[0]}""")
        else:
            db.execute(f"""UPDATE products SET availability = "{y['availability']}", rating = '{rate}' WHERE product_id = {i[0]}""")
        con.commit()

@app.route('/products', methods = ["POST", "GET"])
@login_required
def add():
    session['paserr'] = ""
    session['uperr'] = ""
    session['currentp'] = '/products'
    if request.method == "POST":
        asin = request.form['asin'].upper()
        try:
            product = getall(asin)
        except:
            session['proderr'] = "Product Not Found"
            return redirect('/products')
        title = product['name'].replace('"', "'")
        price = product['price']
        rating = round(float(product['rating']))
        avail = product['availability']
        image = str(product['image'])
        descrip = str(product['descrip']).replace('"', "'")
        disname = product['display_name']
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
            db.execute(f"""INSERT INTO products(asin, name, description, catagory, link, image, creator, employ_name, date, times_clicked, price, rating, availability, display_name) VALUES("{asin}", "{title}", "{descrip}", "{catagory}", "{link}", "{image}", "{creator}", "{employ_name}", "{date.date()}", 0, "{price}", "{rating}", "{avail}", "{disname}")""")
            con.commit()
            return redirect('/products')
        else:
            session['proderr'] = "Please fill out all the details"
            return redirect('/products')
    else:
        if session['frmadmsearch']:
            return render_template('products.html', products = session['products'], err = session['proderr'])
        else:
            con.reconnect()
            db = con.cursor()
            db.execute("SELECT * from products")
            session['products'] = db.fetchall()[::-1]
            return render_template('products.html', products = session['products'], err = session['proderr'])

@app.route('/delete/<int:prod_id>')
def delete(prod_id):
    con.reconnect()
    db = con.cursor()
    db.execute(f"DELETE FROM products WHERE product_id = {prod_id}")
    con.commit()
    return redirect('/products')

@app.route('/updateprice/<int:id>', methods = ["POST", "GET"])
def updateprice(id):
    con.reconnect()
    db = con.cursor()
    if request.method == "POST":
        price = "₹" + request.form['price']
        if price != '₹':
            db.execute(f"UPDATE products SET price = '{price}' WHERE product_id = {id}")
            con.commit()
            return redirect('/products')
        else:
            session['uperr'] = "Price can't be empty"
            return redirect(f'/updateprice/{id}')
    else:
        db.execute(f"SELECT * FROM products WHERE product_id = {id}")
        p = db.fetchall()[0]
        return render_template("addprice.html", p = p, err = session['uperr'])

@app.route('/update/<int:prod_id>', methods = ["POST", "GET"])
def update(prod_id):
    if request.method == "POST":
        asin = request.form['asin'].upper()
        con.reconnect()
        db = con.cursor()
        db.execute(f"SELECT * FROM products WHERE product_id = {prod_id}")
        p = db.fetchall()[0]
        if asin != p[1]:
            try:
                product = getall(asin)
            except:
                session['uperr'] = "Product Not Found"
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
            display_name = product['display_name']
        else:
            link = request.form['amazon-link']
            catagory = request.form.get('product-cata')
            creator = request.form['product-creator']
            employ_name = request.form['employ-name']
            date = datetime.now()
        if asin != "" and link != "" and creator != "" and employ_name != "" and catagory != "none":
            con.reconnect()
            db = con.cursor()
            if asin != p[1]:
                if price == '':
                    db.execute(f"""UPDATE products SET asin = "{asin}", name = "{title}", description = "{descrip}", catagory = "{catagory}", link = "{link}", image = "{image}", creator = "{creator}", employ_name = "{employ_name}", date = "{date.date()}", availability = "{avail}", rating = {rating}, display_name = {display_name} WHERE product_id = "{prod_id}" """)
                else:
                    db.execute(f"""UPDATE products SET asin = "{asin}", name = "{title}", description = "{descrip}", catagory = "{catagory}", link = "{link}", image = "{image}", creator = "{creator}", employ_name = "{employ_name}", date = "{date.date()}", price = "{price}", availability = "{avail}", rating = {rating}, display_name = {display_name} WHERE product_id = "{prod_id}" """)
            else:
                db.execute(f"""UPDATE products SET catagory = "{catagory}", link = "{link}", creator = "{creator}", employ_name = "{employ_name}", date = "{date.date()}" WHERE product_id = "{prod_id}" """)
            con.commit()
            return redirect('/products')
        else:
            session['uperr'] = "Please fill out all the details"
            return redirect(f'/update/{prod_id}')
    else:
        con.reconnect()
        db = con.cursor()
        db.execute(f"SELECT * FROM products WHERE product_id = {prod_id}")
        product = db.fetchall()[0]
        return render_template('update.html', p = product, err = session['uperr'])

if __name__ == "__main__":
    app.run(debug=True)