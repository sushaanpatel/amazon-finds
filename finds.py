from flask import Flask, render_template, request, redirect

app = Flask(__name__)

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
            return redirect('/add')
        else:
            err = "Wrong Password"
    else:
        return render_template('pass-protect.html')

@app.route('/add', methods = ["POST", "GET"])
def add():
    ""

if __name__ == "__main__":
    app.run(debug=True)