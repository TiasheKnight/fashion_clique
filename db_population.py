# import sqlite3
# import random

# # Connect to the SQLite database
# conn = sqlite3.connect('static/db/fc.db')
# c = conn.cursor()

# # List of products to be added to the database (type 'pants')
# pants_products = [
#     ("Classic Tote", 95.00, 'images/pants01.jpg'),
#     ("Classic Tote", 95.00, 'images/pants02.jpg'),
#     ("Baggy Shirt", 55.00, 'images/pants03.jpg'),
#     ("Cotton off-white shirt", 65.00, 'images/pants04.jpg'),
#     ("Handmade crop sweater", 50.00, 'images/pants05.jpg'),
#     ("Handmade crop sweater", 50.00, 'images/pants06.jpg')
# ]

# # Insert each product into the products table
# for product in pants_products:
#     name, price, img = product
#     stock = random.randint(0, 10)  # Random stock between 0 and 10
    
#     c.execute('''
#         INSERT INTO products (name, type, price, img, stock)
#         VALUES (?, ?, ?, ?, ?)
#     ''', (name, 'pants', price, img, stock))

# # Commit the changes and close the connection
# conn.commit()
# conn.close()

# print("Products table populated successfully with 'pants' items!")
import sqlite3
import json
from datetime import datetime

# Define database file path
DB_PATH = 'static/db/fc.db'

def create_tables():
    # Connect to SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            products TEXT NOT NULL, -- JSON string to store cart items
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    print("Tables created successfully.")
    conn.commit()
    conn.close()

def insert_sample_data():
    # Connect to SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Insert sample messages
    sample_messages = [
        ('John Doe', 'john@example.com', 'I have a question about my order.'),
        ('Jane Smith', 'jane@example.com', 'Can you ship internationally?'),
    ]
    cursor.executemany('INSERT INTO messages (full_name, email, message) VALUES (?, ?, ?)', sample_messages)

    # Insert sample orders
    sample_orders = [
        (1, json.dumps([{'product_id': 14, 'quantity': 2}, {'product_id': 15, 'quantity': 1}]), 
         '123 Main St, Cityville, Country', '123-456-7890'),
        (2, json.dumps([{'product_id': 16, 'quantity': 3}]), 
         '456 Park Ave, Metropolis, Country', '987-654-3210'),
    ]
    cursor.executemany('INSERT INTO orders (user_id, products, address, phone) VALUES (?, ?, ?, ?)', sample_orders)

    print("Sample data inserted successfully.")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    insert_sample_data()
