from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json  
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
    try:
        data = request.get_json()  # Receive the data as JSON
        email = data.get('email')
        password = data.get('password')

        # Validate the received data
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required.'}), 400

        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Query the user based on the email
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'success': False, 'message': 'User not found.'}), 404

        stored_password_hash = user[3]  # Assuming password is in the 4th column in the 'users' table (index 3)

        # Hash the entered password using the same hashing algorithm
        hashed_password = hash_password(password)

        # Check if the entered password matches the stored hash
        if hashed_password == stored_password_hash:
            # Store user data in the session (for logged-in users)
            session['user_id'] = user[1]
            session['username'] = user[2]  # Assuming the username is in the second column
            session['email'] = user[4]  # Assuming email is in the third column
            session['phone'] = user[5]
            session['address'] = user[6]
            session['is_logged_in'] = True
            session.modified = True  # Ensure the session is marked as modified
            
            return jsonify({'success': True, 'message': 'Login successful!'}), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid password.'}), 401
        
    except Exception as e:
        print(f"Error during login: {str(e)}")  # Log the actual error
        return jsonify({'success': False, 'message': 'An error occurred during login.'}), 500

    
@app.route('/check_login')
def check_login():
    # Check if 'is_logged_in' is in the session
    if (session.get('is_logged_in') and (session.get('is_logged_in')==True)):  # Default to False if not found
        return jsonify({'logged_in': True, 'user_id': session.get('user_id')})
    else:
        session['is_logged_in'] = False
        return jsonify({'logged_in': False})

@app.route('/logout')
def logout():
    session['username'] = ['Apple']
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

        # Get the current number of entries in the users table to set user_id
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        user_id = user_count + 1  # Set the new user_id to the next available number

        # Insert the new user into the database, including user_id
        cursor.execute('''INSERT INTO users (user_id, username, email, password) 
                          VALUES (?, ?, ?, ?)''', (user_id, name, email, hashed_password))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Registration successful!'}), 200

    except Exception as e:
        print(f"Error during registration: {str(e)}")  # Log the actual error
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
    print(session)
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

    # Get the number of unique products in the cart
    cart_count = len(session['cart'])

    # Return the updated cart and cart count
    return jsonify({'success': True, 'cart': session['cart'], 'cart_count': cart_count})

@app.route('/get_cart', methods=['GET'])
def get_cart():
    cart = session.get('cart', [])
    return jsonify({'cart': cart})


def clear_cart():
    session['cart'] = []
    session.modified = True  # Mark the session as modified to ensure it is saved



from flask import redirect, url_for

@app.route('/update_quantity', methods=['POST']) 
def update_quantity():
    try:
        data = request.get_json()
        product_id = str(data['product_id'])
        quantity = int(data['quantity'])
        price = float(data['price'])  # Retrieve price from the request

        # Check if the cart exists in the session
        if 'cart' not in session:
            return jsonify({'error': 'Cart is empty'}), 400

        # Find the product in the cart and update its quantity and total
        for item in session['cart']:
            if str(item['product_id']) == product_id:
                item['quantity'] = quantity
                item['price'] = price  # Ensure price is updated
                item['total'] = price * quantity  # Update total
                session.modified = True
                break
        else:
            return jsonify({'error': 'Product not found in cart'}), 404

        # Redirect to the cart page
        return redirect(url_for('cart'))  # Replace 'cart' with your cart route function name

    except KeyError as e:
        return jsonify({'error': f'Missing key: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500




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
    print(f"Session data: {session}") 
    username = session['username']  # Get the logged-in user's name 
    
    # Connect to the database and fetch user details
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT username, email, phone, address FROM users WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    
    conn.close()
    print(f"User data: {user_data}") 
    if user_data:
        # Return the user data to the frontend as a JSON response
        return jsonify({
            'status': 'success',
            'user_data': {
                'name': user_data[0],
                'email': user_data[1],
                'phone': user_data[2],
                'address': user_data[3]
            }
        })
    else:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

import hashlib

def hash_password(password: str) -> str:
    """Hashes the given password using SHA256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

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

    # If a password is provided, hash it and update it
    if password:
        hashed_password = hash_password(password)
        cursor.execute(""" 
            UPDATE users 
            SET username = ?, email = ?, phone = ?, password = ? 
            WHERE id = ? 
        """, (name, email, phone, hashed_password, user_id))
    else:
        cursor.execute("""
            UPDATE users 
            SET username = ?, email = ?, phone = ? 
            WHERE id = ? 
        """, (name, email, phone, user_id))
    
    # Update session values
    session['username'] = name  # Store username in session
    session['email'] = email    # Store email in session

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



@app.route('/account', methods=['GET'])
def account():
    if 'user_id' not in session:
        return redirect('/login_P')  # Redirect to login page if not logged in
    
    user_id = session['user_id']  # Get the logged-in user's ID
    
    # Connect to the database and fetch user details
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT username, email, phone FROM users WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()
    
    conn.close()
    
    # Debugging: Check if the user data is being retrieved
    print(f"User data: {user_data}")
    if user_data:
        # Render the account page with user data
        return render_template('account.html', user_data=user_data)
    else:
        return render_template('error.html', message="User not found")
    

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
    app.run(host='0.0.0.0', port=80, debug=True)
