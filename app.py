from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from flask_mysqldb import MySQL
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import ai_recommendations

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'supersecretkey'


# -----------------MySQL Config----------------------

#Loads database credentials from .env and sets up MySQL connection.
load_dotenv()
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)


# ------------------ Routes to pages ------------------

#Shows login page
@app.route('/')
def login_page():
    return render_template('login.html')
@app.route('/login')
def login_page_alias():
    return render_template('login.html')

#Shows Registration page
@app.route('/register')
def register_page():
    return render_template('register.html')

#Loads customer page only if user is a customer.
@app.route('/customer')
def customer_page():
    if session.get('role') != 'customer':
        return redirect(url_for('login_page'))
    return render_template('customer.html')

#Loads reatiler page only if user is a retailer
@app.route('/retailer')
def retailer_page():
    if session.get('role') != 'retailer':
        return redirect(url_for('login_page'))
    return render_template('retailer.html')

#Logs user out
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

#Loads retailer add product form
@app.route('/retailer/add-product')
def retailer_add_product():
    if session.get('role') != 'retailer':
        return redirect(url_for('login_page'))
    return render_template('retailer_add_product.html')



# ------------------ Auth Logic ------------------

#Registers a new user into the users table after hashing their password.
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data['name']
    email = data['email']
    password = generate_password_hash(data['password'])
    role = data['role']

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                    (name, email, password, role))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Registered successfully'}), 201
    except Exception as e:
        print("Register error:", e)
        return jsonify({'error': 'Registration failed. Email might already exist.'}), 400

#Authenticates user and sets session data if credentials are valid.
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id, name, password, role FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()

    if user and check_password_hash(user[2], password):
        session['user_id'] = user[0]
        session['name'] = user[1]
        session['role'] = user[3]
        return jsonify({'message': 'Login successful', 'role': user[3]})
    else:
        return jsonify({'error': 'Invalid email or password'}), 401



# ------------------recommendation logic---------------------------

#Fetches all products, identifies the current one, and returns AI-based recommendations.
@app.route('/recommendations/<int:product_id>')
def get_recommendations(product_id):
    try:
        # Fetch all products
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM products")
        rows = cur.fetchall()

        all_products = [{
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'price': float(row[3]),
            'category': row[4],
            'stock_quantity': row[5],
            'image_url': row[6]
        } for row in rows]

        # Find the current product
        current_product = next((p for p in all_products if p['id'] == product_id), None)
        if not current_product:
            return jsonify({'error': 'Product not found'}), 404

        # Get recommendations
        recs = ai_recommendations.get_recommendations(current_product, all_products)
        return jsonify(recs)
    except Exception as e:
        print("Recommendation error:", e)
        return jsonify([])



# -----------------product endpoints-----------------------------------

#Returns all product details including thumbnails as a JSON list.
@app.route('/products', methods=['GET'])
def get_products():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()

    product_list = [{
        'id': row[0],
        'name': row[1],
        'description': row[2],
        'price': float(row[3]),
        'category': row[4],
        'stock_quantity': row[5],
        'image_url': row[6],
        'thumb_url': row[8]  # 👈 NEW
    } for row in products]

    return jsonify(product_list)

#Adds a new product to the database using JSON data.
@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    cur = mysql.connection.cursor()
    cur.execute("""INSERT INTO products (name, description, price, category, stock_quantity, image_url)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (data['name'], data['description'], data['price'],
                 data['category'], data['stock_quantity'], data['image_url']))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Product added successfully'}), 201

#Updates product details like name, price, stock, and description.
@app.route('/update-product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    stock_quantity = data.get('stock_quantity')
    description = data.get('description')
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE products
        SET name = %s, price = %s, stock_quantity = %s, description = %s
        WHERE product_id = %s
    """, (name, price, stock_quantity, description, product_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Product updated successfully'})

#Returns full details of a specific product by ID.
@app.route('/products/<int:product_id>')
def get_product_detail(product_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    row = cur.fetchone()
    cur.close()

    if not row:
        return jsonify({'error': 'Product not found'}), 404

    product = {
        'id': row[0],
        'name': row[1],
        'description': row[2],
        'price': float(row[3]),
        'category': row[4],
        'stock_quantity': row[5],
        'image_url': row[6]
    }
    return jsonify(product)



# -----------------------cart----------------------------------------------

#Adds selected product to the cart with quantity for the current user.
@app.route('/cart')
def get_cart():
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT c.cart_id, c.product_id, p.name, p.price, c.quantity, p.stock_quantity
        FROM cart c JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = %s
    """, (user_id,))
    items = cur.fetchall()
    cur.close()

    return jsonify([{
        'cart_id': i[0],
        'product_id': i[1],
        'name': i[2],
        'price': float(i[3]),
        'quantity': i[4],
        'stock_quantity': i[5]
        }for i in items])

#Fetches current user's cart details including joined product info.
@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity') or 1  # default fallback to 1
    user_id = session['user_id']

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO cart (user_id, product_id, quantity)
        VALUES (%s, %s, %s)
    """, (user_id, product_id, quantity))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Added to cart'}), 201

#Finalizes purchase: checks stock, calculates total, adds order, reduces stock, clears cart.
@app.route('/cart/checkout', methods=['POST'])
def checkout():
    user_id = session.get('user_id')

    # Fetch cart
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT c.product_id, p.name, p.price, c.quantity, p.stock_quantity
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = %s
    """, (user_id,))
    items = cur.fetchall()

    if not items:
        return jsonify({'error': 'Cart is empty'}), 400

    # Check stock and calculate total
    total = 0
    for product_id, name, price, quantity, stock_quantity in items:
        if quantity > stock_quantity:
            mysql.connection.rollback()
            return jsonify({'error': f'Not enough stock for {name}'}), 400
        total += price * quantity

    # Insert into orders table
    cur.execute("INSERT INTO orders (user_id, total_amount) VALUES (%s, %s)", (user_id, total))
    order_id = cur.lastrowid

    # Reduce stock
    for product_id, _, _, quantity, _ in items:
        cur.execute("UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s", (quantity, product_id))

    # Clear cart
    cur.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Order placed!', 'order_id': order_id}), 200



# ---------------------image-upload---------------------

#Sets upload directory and checks for valid image extensions.
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
from PIL import Image

#Handles product image upload, creates thumbnail, and saves product info in DB.
@app.route('/upload-product', methods=['POST'])
def upload_product():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file'}), 400

    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid image file'}), 400

    filename = secure_filename(file.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(image_path)

    # 🔹 Generate thumbnail (max 300x300)
    thumb_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails')
    os.makedirs(thumb_dir, exist_ok=True)
    thumb_path = os.path.join(thumb_dir, filename)

    try:
        image = Image.open(image_path)
        image.thumbnail((300, 300))
        image.save(thumb_path)
    except Exception as e:
        print("Thumbnail creation error:", e)
        return jsonify({'error': 'Image processing failed'}), 500

    #  Get form fields
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    category = request.form.get('category')
    stock_quantity = request.form.get('stock_quantity')

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO products (name, description, price, category, stock_quantity, image_url, thumb_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            name,
            description,
            price,
            category,
            stock_quantity,
            filename,
            f'thumbnails/{filename}'
        ))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Product added successfully'}), 201
    except Exception as e:
        print("Product upload error:", e)
        return jsonify({'error': 'Failed to add product'}), 500



#------------------checkout-------------------

#Renders the checkout HTML page for customers only.
@app.route('/checkout')
def checkout_page():
    if session.get('role') != 'customer':
        return redirect(url_for('login_page'))
    return render_template('checkout.html')

#Removes a specific item from user's cart.
@app.route('/cart/remove/<int:cart_id>', methods=['DELETE'])
def remove_from_cart(cart_id):
    user_id = session.get('user_id')
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM cart WHERE cart_id = %s AND user_id = %s", (cart_id, user_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Item removed from cart'})



#-----------------Customer Order View--------------------

#Displays a list of past orders for logged-in customer.
@app.route('/orders')
def view_orders():
    user_id = session.get('user_id')
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT order_id, order_date, total_amount, status
        FROM orders
        WHERE user_id = %s
        ORDER BY order_date DESC
    """, (user_id,))
    orders = cur.fetchall()
    cur.close()

    return render_template('orders.html', orders=orders)

#Shows a summary of a specific order for the customer.
@app.route('/order-summary/<int:order_id>')
def order_summary(order_id):
    user_id = session.get('user_id')
    cur = mysql.connection.cursor()

    cur.execute("SELECT order_id, order_date, total_amount, status FROM orders WHERE order_id = %s AND user_id = %s", (order_id, user_id))
    order = cur.fetchone()

    cur.close()
    if not order:
        return "Order not found or unauthorized", 404

    return render_template('order_summary.html', order=order)



#----------------- Retailer Order Management ----------------------------

#Retailer view to see all orders placed by customers.
@app.route('/retailer/orders')
def manage_orders():
    if session.get('role') != 'retailer':
        return redirect(url_for('login_page'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT o.order_id, u.name, o.order_date, o.total_amount, o.status
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        ORDER BY o.order_date DESC
    """)
    orders = cur.fetchall()
    cur.close()
    return render_template('retailer_orders.html', orders=orders)

#Allows retailer to update the order status (e.g.Pending, Shipped, Delivered)
@app.route('/retailer/orders/update/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    if session.get('role') != 'retailer':
        return redirect(url_for('login_page'))
    
    new_status = request.form.get('status')
    cur = mysql.connection.cursor()
    cur.execute("UPDATE orders SET status = %s WHERE order_id = %s", (new_status, order_id))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('manage_orders'))

#Allows retailer to delete a specific customer order.
@app.route('/retailer/orders/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    if session.get('role') != 'retailer':
        return redirect(url_for('login_page'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('manage_orders'))



# ----------------------main-------------------------
if __name__ == '__main__':
    app.run(debug=True)

