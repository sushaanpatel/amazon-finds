from flask import Flask, render_template, request, redirect
import mysql.connector
from datetime import datetime

app = Flask(__name__)
con = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "password",
    database = "amazonfinds"
)

global err
err = ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin', methods = ["POST", "GET"])
def admin():
    global err
    if request.method == "POST":
        password = request.form['password']
        if password == "1234":
            return redirect('/products')
        else:
            err = "Wrong Password"
    else:
        return render_template('pass-protect.html')

@app.route('/products', methods = ["POST", "GET"])
def add():
    if request.method == "POST":
        title = request.form['product-name']
        descrip = request.form['product-description']
        price = request.form['product-price']
        image = request.files['product-image']
        creator = request.form['product-creator']
        employ_name = request.form['employ-name']
        date = datetime.now()
        con.reconnect()
        db = con.cursor()
        db.execute(f"""INSERT INTO products(name, description, price, image, creator, employ_name, date, times_clicked) VALUES("{title}", "{descrip}", "{price}", "{image.filename}", "{creator}", "{employ_name}", "{date.date()}", 0)""")
        con.commit()
        return redirect('/add')
    else:
        con.reconnect()
        db = con.cursor()
        db.execute("SELECT * from products")
        product_list = db.fetchall()
        return render_template('products.html', products = product_list)

if __name__ == "__main__":
    app.run(debug=True)