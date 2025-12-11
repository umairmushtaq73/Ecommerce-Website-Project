from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key-12345-change-this-in-production'
app.config['SECRET_KEY'] = 'your-secret-key-12345-change-this-in-production'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# File paths
PRODUCTS_FILE = 'products.json'
ORDERS_FILE = 'orders.json'
USERS_FILE = 'users.json'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, email, name):
        self.id = id
        self.email = email
        self.name = name

# Initialize data files
def init_files():
    for file_path in [PRODUCTS_FILE, ORDERS_FILE, USERS_FILE]:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump([], f)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    users = read_users()
    for user in users:
        if str(user['id']) == user_id:
            return User(str(user['id']), user['email'], user['name'])
    return None

# File operations
def read_products():
    with open(PRODUCTS_FILE, 'r') as f:
        return json.load(f)

def write_products(products):
    with open(PRODUCTS_FILE, 'w') as f:
        json.dump(products, f, indent=4)

def read_orders():
    with open(ORDERS_FILE, 'r') as f:
        return json.load(f)

def write_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=4)

def read_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def write_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def init_cart():
    if 'cart' not in session:
        session['cart'] = []

# Routes
@app.route('/')
def index():
    products = read_products()
    return render_template('index.html', products=products)

# Authentication Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        users = read_users()
        
        # Check if user already exists
        for user in users:
            if user['email'] == email:
                flash('Email already registered!', 'error')
                return redirect(url_for('register'))
        
        # Create new user
        new_user = {
            'id': len(users) + 1,
            'name': name,
            'email': email,
            'password': generate_password_hash(password),
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        users.append(new_user)
        write_users(users)
        
        # Log the user in
        user_obj = User(str(new_user['id']), email, name)
        login_user(user_obj)
        
        flash('Registration successful! Welcome to ShopEasy!', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        users = read_users()
        
        for user in users:
            if user['email'] == email and check_password_hash(user['password'], password):
                user_obj = User(str(user['id']), email, user['name'])
                login_user(user_obj)
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
        
        flash('Invalid email or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    # Get user orders
    orders = read_orders()
    user_orders = [order for order in orders if order.get('user_id') == current_user.id]
    
    return render_template('profile.html', user=current_user, orders=user_orders)

# Products CRUD
@app.route('/products')
def products():
    products_list = read_products()
    return render_template('products.html', products=products_list)

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        products = read_products()
        
        new_product = {
            'id': len(products) + 1,
            'name': request.form['name'],
            'description': request.form['description'],
            'price': float(request.form['price']),
            'quantity': int(request.form['quantity']),
            'category': request.form['category'],
            'image': request.form.get('image', '/static/images/default-product.jpg')
        }
        
        products.append(new_product)
        write_products(products)
        flash('Product added successfully!', 'success')
        return redirect(url_for('products'))
    
    return render_template('add_product.html')

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    products = read_products()
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('products'))
    
    if request.method == 'POST':
        product['name'] = request.form['name']
        product['description'] = request.form['description']
        product['price'] = float(request.form['price'])
        product['quantity'] = int(request.form['quantity'])
        product['category'] = request.form['category']
        product['image'] = request.form.get('image', '/static/images/default-product.jpg')
        
        write_products(products)
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products'))
    
    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:product_id>')
@login_required
def delete_product(product_id):
    products = read_products()
    products = [p for p in products if p['id'] != product_id]
    write_products(products)
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products'))

# Shopping Cart
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    init_cart()
    products = read_products()
    product = next((p for p in products if p['id'] == product_id), None)
    
    if product:
        cart = session['cart']
        found = False
        
        for item in cart:
            if item['id'] == product_id:
                item['quantity'] += 1
                found = True
                break
        
        if not found:
            cart_item = {
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'quantity': 1,
                'image': product.get('image', '/static/images/default-product.jpg')
            }
            cart.append(cart_item)
        
        session['cart'] = cart
        flash(f'{product["name"]} added to cart!', 'success')
    
    return redirect(request.referrer or url_for('index'))

@app.route('/cart')
def view_cart():
    init_cart()
    cart = session['cart']
    total_price = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total_price=total_price)

@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    init_cart()
    cart = session['cart']
    quantity = int(request.form['quantity'])
    
    for item in cart:
        if item['id'] == product_id:
            if quantity > 0:
                item['quantity'] = quantity
            else:
                cart.remove(item)
            break
    
    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    init_cart()
    cart = session['cart']
    cart = [item for item in cart if item['id'] != product_id]
    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/clear_cart')
def clear_cart():
    session['cart'] = []
    return redirect(url_for('view_cart'))

# Orders
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    init_cart()
    cart = session['cart']
    
    if not cart:
        flash('Your cart is empty!', 'error')
        return redirect(url_for('view_cart'))
    
    if request.method == 'POST':
        orders = read_orders()
        
        new_order = {
            'order_id': len(orders) + 1,
            'user_id': current_user.id,
            'customer_name': request.form['name'],
            'email': request.form['email'],
            'address': request.form['address'],
            'phone': request.form['phone'],
            'items': cart.copy(),
            'total': sum(item['price'] * item['quantity'] for item in cart),
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'Pending'
        }
        
        orders.append(new_order)
        write_orders(orders)
        session['cart'] = []
        
        flash(f'Order #{new_order["order_id"]} placed successfully!', 'success')
        return redirect(url_for('profile'))
    
    total_price = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('checkout.html', cart=cart, total_price=total_price)

@app.route('/orders')
@login_required
def view_orders():
    orders = read_orders()
    user_orders = [order for order in orders if order.get('user_id') == current_user.id]
    return render_template('orders.html', orders=user_orders)

# Initialize files
init_files()

if __name__ == '__main__':
    app.run(debug=True)