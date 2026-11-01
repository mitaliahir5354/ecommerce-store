from flask import Flask, render_template, request, redirect, session
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret123'
# ---------------- DATABASE ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(200))
    price = db.Column(db.Integer)
    image = db.Column(db.String(200))

# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=['GET','POST'])
def register():
    error = None

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # 🚨 Check empty fields
        if name == "" or email == "" or password == "":
            error = "All fields are required!"

        else:
            # check if email already exists
            existing_user = User.query.filter_by(email=email).first()

            if existing_user:
                error = "Email already registered!"
            else:
                user = User(name=name, email=email, password=password)
                db.session.add(user)
                db.session.commit()
                return redirect('/login')

    return render_template("register.html", error=error)

@app.route('/login', methods=['GET','POST'])
def login():
    error = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # 🚨 Check empty fields
        if email == "" or password == "":
            error = "Please enter email and password"

        else:
            user = User.query.filter_by(email=email, password=password).first()

            if user:
                return redirect('/products')
            else:
                error = "Invalid email or password"

    return render_template("login.html", error=error)

@app.route('/products')
def products():
    products = Product.query.all()
    return render_template("products.html", products=products)

@app.route('/add_product', methods=['GET','POST'])
def add_product():
    if request.method == 'POST':
        p = Product(
            name=request.form['name'],
            description=request.form['description'],
            price=request.form['price'],
            image=request.form['image']
        )
        db.session.add(p)
        db.session.commit()
        return redirect('/products')
    return render_template("add_product.html")

@app.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get(id)
    return render_template("product_detail.html", product=product)

@app.route('/delete_product/<int:id>')
def delete_product(id):
    product = Product.query.get(id)

    if product:
        db.session.delete(product)
        db.session.commit()

    return redirect('/products')

@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append(id)
    session.modified = True

    return redirect('/cart')

@app.route('/cart')
def cart():
    cart_items = []

    if 'cart' in session:
        for item_id in session['cart']:
            product = Product.query.get(item_id)
            if product:
                print(product.image)   
                cart_items.append(product)

    return render_template('cart.html', cart=cart_items)

@app.route('/remove_from_cart/<int:id>')
def remove_from_cart(id):
    if 'cart' in session:
        session['cart'].remove(id)
        session.modified = True

    return redirect('/cart')

@app.route('/logout')
def logout():
    session.clear()   # removes all session data
    return redirect('/')

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)