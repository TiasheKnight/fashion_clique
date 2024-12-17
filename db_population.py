import sqlite3
import random

# Connect to the SQLite database
conn = sqlite3.connect('static/db/fc.db')
c = conn.cursor()

# List of products to be added to the database (type 'pants')
pants_products = [
    ("Classic Tote", 95.00, 'images/pants01.jpg'),
    ("Classic Tote", 95.00, 'images/pants02.jpg'),
    ("Baggy Shirt", 55.00, 'images/pants03.jpg'),
    ("Cotton off-white shirt", 65.00, 'images/pants04.jpg'),
    ("Handmade crop sweater", 50.00, 'images/pants05.jpg'),
    ("Handmade crop sweater", 50.00, 'images/pants06.jpg')
]

# Insert each product into the products table
for product in pants_products:
    name, price, img = product
    stock = random.randint(0, 10)  # Random stock between 0 and 10
    
    c.execute('''
        INSERT INTO products (name, type, price, img, stock)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, 'pants', price, img, stock))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Products table populated successfully with 'pants' items!")
