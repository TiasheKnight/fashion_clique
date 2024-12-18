from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import hashlib

app = Flask(__name__, static_folder='static')
app.secret_key = 'whatever'  # Replace this with a more secure key in production

# Function to hash passwords securely
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

@app.route('/')
def home():
    return render_template('index.html')

# Path to your database
DB_PATH = 'static/db/fc.db'

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Query the database to check for user credentials
    cursor.execute("SELECT id, username, password FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()  # Fetch the user

    conn.close()

    # Check if the user exists and password matches
    if user and user[2] == password:
        session['username'] = user[1]  # Store username in session
        session['email'] = email      # Store email in session
        session['is_logged_in'] = True  # Explicitly mark as logged in
        
        # Return success response
        return jsonify({'status': 'success', 'message': 'Login successful'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401



    
@app.route('/check_login')
def check_login():
    # Check if 'is_logged_in' is in the session
    if session.get('is_logged_in'):  # Default to False if not found
        return jsonify({'logged_in': True, 'user_id': session.get('user_id')})
    else:
        return jsonify({'logged_in': False})





@app.route('/logout')
def logout():
    session['username'] = []
    session['is_logged_in'] = False
    session.modified = True  # Mark the session as modified to ensure it is saved
    return redirect(url_for('login'))

@app.route('/register', methods=['POST'])
def register():
    try:
        # Get the data from the request as JSON
        data = request.get_json()

        # Extract fields from the request data
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        # Validate the received data
        if not name or not email or not password:
            return jsonify({'success': False, 'message': 'All fields are required.'}), 400

        # Hash the password
        hashed_password = hash_password(password)

        # Create a new user in the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if the email already exists
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({'success': False, 'message': 'Email already registered.'}), 400

        # Insert the new user into the database
        cursor.execute('''INSERT INTO users (username, email, password) 
                          VALUES (?, ?, ?)''', (name, email, hashed_password))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Registration successful!'}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred during registration.'}), 500

    
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    full_name = data.get('full_name')
    email = data.get('email')
    message = data.get('message')

    if not full_name or not email or not message:
        return jsonify({'status': 'error', 'message': 'All fields are required'}), 400

    # Insert into database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (full_name, email, message) VALUES (?, ?, ?)",
            (full_name, email, message)
        )
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Message sent successfully!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/submit_order', methods=['POST'])
def submit_order():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'You must be logged in to place an order.'}), 401

    data = request.get_json()
    address = data.get('address')
    phone = data.get('phone')
    products = json.dumps(session.get('cart', []))  # Convert cart to JSON string
    user_id = session['user_id']

    # Insert order into database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO orders (user_id, products, address, phone)
        VALUES (?, ?, ?, ?)
    """, (user_id, products, address, phone))
    conn.commit()
    conn.close()

    # Clear the cart after placing an order
    clear_cart()

    return jsonify({'status': 'success', 'message': 'Order placed successfully!'})



    
# Function to get products from the database with type filter
def get_products(product_type):
    # Connect to the SQLite database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # If a product type is provided, filter by type
    if product_type:
        c.execute("SELECT * FROM products WHERE type=?", (product_type,))
        
    products = c.fetchall()  # Fetch all rows
    conn.close()
    return products

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form['product_id']  # Get the product_id from the form
    quantity = 1  # Default quantity if not specified
    if 'quantity' in request.form:
        quantity = int(request.form['quantity'])  # Get the quantity if specified
    
    if 'cart' not in session:
        session['cart'] = []  # Initialize the cart if it doesn't exist
    
    # Check if product already exists in the cart
    product_found = False
    for item in session['cart']:
        if isinstance(item, dict) and item.get('product_id') == int(product_id):
            item['quantity'] += quantity  # Update the quantity if the product is already in the cart
            product_found = True
            break
    
    if not product_found:
        # Add new product to the cart with the specified quantity
        session['cart'].append({"product_id": int(product_id), "quantity": quantity})

    session.modified = True  # Mark session as modified to ensure changes are saved
    print(session)
    return jsonify({'success': True, 'cart': session['cart']})

def clear_cart():
    """Clears the cart from the session."""
    session['cart'] = []
    session.modified = True  # Mark the session as modified to ensure it is saved



@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    try:
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])  # Get the new quantity

        # Check if the cart exists in the session
        if 'cart' not in session:
            return jsonify({'error': 'Cart is empty'}), 400

        # Find the product in the cart and update its quantity
        for item in session['cart']:
            if item['product_id'] == product_id:
                item['quantity'] = quantity  # Update quantity
                session.modified = True
                return jsonify({'success': True, 'cart': session['cart']})

        return jsonify({'error': 'Product not found in cart'}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while updating the cart'}), 500



@app.route('/cart')
def cart():
    # Retrieve cart items (which are dictionaries with 'product_id' and 'quantity')
    cart_items = session.get('cart', [])
    
    # Fetch product details from the database
    products = []
    total_price = 0
    
    # Connect to the database and retrieve products
    conn = sqlite3.connect('static/db/fc.db')
    cursor = conn.cursor()

    for item in cart_items:
        product_id = item['product_id']  # Extract product_id from the dictionary

        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()

        if product:
            product_name = product[1]
            product_price = product[3]
            product_image = product[4]
            
            # Get the quantity from the cart item (instead of hardcoding it)
            quantity = item['quantity']

            total_price += product_price * quantity  # Calculate total price

            products.append({
                'id': product_id,
                'name': product_name,
                'price': product_price,
                'image': product_image,
                'quantity': quantity,
                'total': product_price * quantity
            })

    conn.close()  # Close the database connection

    return render_template('cart.html', products=products, total_price=total_price)


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    product_id = int(request.form['product_id'])  # Get the product_id from the form and convert to integer

    # If the 'cart' exists in the session, we proceed to remove the item
    if 'cart' in session:
        # Loop through the cart to find the item with the matching product_id
        for item in session['cart']:
            if item['product_id'] == product_id:
                session['cart'].remove(item)  # Remove the product object from the cart
                session.modified = True  # Ensure the session is updated
                return jsonify({'status': 'success', 'message': 'Item removed'})

    # If product_id was not found in the cart
    return jsonify({'status': 'error', 'message': 'Item not found'})

@app.route('/details') 
def details():      
    username = session['username']  # Get the logged-in user's name 
    
    # Connect to the database and fetch user details
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT username, email, phone FROM users WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    
    conn.close()
    
    if user_data:
        # Return the user data to the frontend as a JSON response
        return jsonify({
            'status': 'success',
            'user_data': {
                'name': user_data[0],
                'email': user_data[1],
                'phone': user_data[2]
            }
        })
    else:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

@app.route('/update_account', methods=['POST'])
def update_account():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'You must be logged in to update your account.'}), 401

    # Get the updated data from the form submission
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')

    user_id = session['user_id']

    # Connect to the database and update the user details
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Update the user data, if password is provided, update it too
    if password:
        cursor.execute("""
            UPDATE users 
            SET username = ?, email = ?, phone = ?, password = ? 
            WHERE id = ?
        """, (name, email, phone, password, user_id))
    else:
        cursor.execute("""
            UPDATE users 
            SET username = ?, email = ?, phone = ? 
            WHERE id = ?
        """, (name, email, phone, user_id))
    session['username'] = name  # Store username in session
    session['email'] = email      # Store email in session

    conn.commit()

    # Fetch the updated data to return to the client
    cursor.execute("SELECT username, email, phone FROM users WHERE id = ?", (user_id,))
    updated_user_data = cursor.fetchone()
    conn.close()

    return jsonify({
        'status': 'success',
        'user_data': {
            'name': updated_user_data[0],
            'email': updated_user_data[1],
            'phone': updated_user_data[2]
        }
    })


@app.route('/account')
def account():
    if 'is_logged_in' not in session:
        return redirect(url_for('login_P'))  # Redirect to login if not logged in
    return render_template('account.html')

# Route for the register page
@app.route('/register_P')
def register_P():
    return render_template('register.html')

# Route for the contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Route for the dresses page
@app.route('/dresses')
def dresses():
    products = get_products("dress") 
    return render_template('dresses.html', products=products)

# Route for the login page
@app.route('/login_P')
def login_P():
    return render_template('login.html')

# Route for the top page
@app.route('/top')
def top():
    products = get_products("top") 
    return render_template('top.html', products=products)

@app.route('/pants') 
def pants(): 
    products = get_products("pants") 
    return render_template('pants.html', products=products)

@app.route('/index')  
def index(): 
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
