from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'whatever'  # Replace this with a more secure key in production

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    # This should be replaced with actual authentication logic (e.g., database lookup)
    if email == 'test@example.com' and password == 'password':
        session['logged_in'] = True
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})
    
@app.route('/check_login')
def check_login():
    return jsonify({'logged_in': 'logged_in' in session})

@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Remove 'logged_in' from session to log out
    return redirect(url_for('home'))  # Redirect to the home page after logout

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data['name']
    email = data['email']
    password = data['password']

    # Simulate account creation (you can replace this with real logic)
    if name and email and password:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})
    
# Function to get products from the database with type filter
def get_products(product_type):
    # Connect to the SQLite database
    conn = sqlite3.connect('static/db/fc.db')
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
    if 'cart' not in session:
        session['cart'] = []  # Initialize the cart if it doesn't exist
    
    session['cart'].append(product_id)  # Add product ID to the cart
    session.modified = True  # Mark session as modified to ensure changes are saved
    
    return jsonify({'success': True, 'cart': session['cart']})



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
    # Retrieve product_ids stored in the session
    cart_items = session.get('cart', [])
    
    # Fetch product details from the database
    products = []
    total_price = 0
    
    # Connect to the database and retrieve products
    conn = sqlite3.connect('static/db/fc.db')
    cursor = conn.cursor()

    for product_id in cart_items:
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        
        if product:
            product_name = product[1]
            product_price = product[3]
            product_image = product[4]
            
            # Assuming you're keeping track of the quantity in the session as well
            # If not, you can hardcode it as 1 for now
            quantity = 1  # Or fetch quantity if you store it in the session
            
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




def remove_from_cart():
    product_id = request.form['product_id']
    
    # Ensure the cart exists in the session
    if 'cart' in session:
        # Loop through the cart and remove the item with the matching product ID
        session['cart'] = [item for item in session['cart'] if item['product_id'] != product_id]
        session.modified = True  # Mark session as modified

    # Return a success message
    return jsonify({'success': True})


@app.route('/account')
def account():
    if 'logged_in' not in session:
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
