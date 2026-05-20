import random
from datetime import datetime, timedelta
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="pri",  # apna MySQL password daalo
    database="sales_db"
)
cursor = conn.cursor()

cities = [
    ('Delhi', 'North'), ('Noida', 'North'),
    ('Mumbai', 'West'), ('Pune', 'West'),
    ('Chennai', 'South'), ('Bangalore', 'South'),
    ('Kolkata', 'East'), ('Jaipur', 'North'),
    ('Hyderabad', 'South'), ('Ahmedabad', 'West')
]
names = [
    'Rahul Sharma', 'Priya Singh', 'Amit Kumar',
    'Neha Gupta', 'Vikram Rao', 'Pooja Patel',
    'Ravi Verma', 'Sneha Joshi', 'Arjun Nair',
    'Ananya Das', 'Karan Mehta', 'Divya Reddy',
    'Suresh Iyer', 'Meera Pillai', 'Rohit Yadav'
]

print("Inserting customers...")
for i in range(200):
    name = random.choice(names) + f" {i}"
    email = f"user{i}@gmail.com"
    city, region = random.choice(cities)
    cursor.execute("""
        INSERT INTO customers (name, email, city, region)
        VALUES (%s, %s, %s, %s)
    """, (name, email, city, region))
conn.commit()
print("✅ 200 customers done")

categories = [
    'Electronics', 'Clothing', 'Books',
    'Home & Kitchen', 'Sports', 'Beauty',
    'Toys', 'Grocery'
]
for cat in categories:
    cursor.execute(
        "INSERT IGNORE INTO categories (category_name) VALUES (%s)",
        (cat,)
    )
conn.commit()

cursor.execute("SELECT category_id, category_name FROM categories")
cat_map = {name: cid for cid, name in cursor.fetchall()}

products = [
    ('Laptop 15 inch', 'Electronics', 45000),
    ('Smartphone Pro', 'Electronics', 25000),
    ('Wireless Headphones', 'Electronics', 2999),
    ('Smart Watch', 'Electronics', 8999),
    ('Bluetooth Speaker', 'Electronics', 1999),
    ('USB Hub', 'Electronics', 799),
    ('Men T-Shirt', 'Clothing', 499),
    ('Women Kurti', 'Clothing', 799),
    ('Jeans', 'Clothing', 1299),
    ('Jacket', 'Clothing', 2499),
    ('Sneakers', 'Clothing', 1999),
    ('Python Programming', 'Books', 599),
    ('Data Science Guide', 'Books', 799),
    ('Machine Learning Book', 'Books', 699),
    ('Web Development', 'Books', 499),
    ('Mixer Grinder', 'Home & Kitchen', 3499),
    ('Pressure Cooker', 'Home & Kitchen', 1299),
    ('Air Fryer', 'Home & Kitchen', 5999),
    ('Water Bottle', 'Home & Kitchen', 399),
    ('Cricket Bat', 'Sports', 1599),
    ('Football', 'Sports', 699),
    ('Yoga Mat', 'Sports', 599),
    ('Dumbbells Set', 'Sports', 1999),
    ('Face Wash', 'Beauty', 199),
    ('Moisturizer', 'Beauty', 349),
    ('Perfume', 'Beauty', 999),
    ('Lego Set', 'Toys', 1499),
    ('Board Game', 'Toys', 799),
    ('Basmati Rice 5kg', 'Grocery', 399),
    ('Green Tea', 'Grocery', 199),
]

print("Inserting products...")
for pname, pcat, pprice in products:
    stock = random.randint(20, 200)
    cursor.execute("""
        INSERT INTO products
        (product_name, category_id, price, stock)
        VALUES (%s, %s, %s, %s)
    """, (pname, cat_map[pcat], pprice, stock))
conn.commit()
print("✅ Products done")

cursor.execute("SELECT product_id, price FROM products")
product_data = cursor.fetchall()

cursor.execute("SELECT customer_id FROM customers")
customer_ids = [row[0] for row in cursor.fetchall()]

statuses = [
    'delivered', 'delivered', 'delivered',
    'shipped', 'processing', 'cancelled'
]

start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 12, 31)

print("Inserting 1000 orders...")
for i in range(1000):
    customer_id = random.choice(customer_ids)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    order_date = start_date + timedelta(days=random_days)
    status = random.choice(statuses)
    num_items = random.randint(1, 4)
    selected = random.sample(product_data, num_items)
    total_amount = sum(
        float(price) * random.randint(1, 3)
        for _, price in selected
    )
    cursor.execute("""
        INSERT INTO orders
        (customer_id, order_date, status, total_amount)
        VALUES (%s, %s, %s, %s)
    """, (customer_id,
          order_date.strftime('%Y-%m-%d'),
          status,
          round(total_amount, 2)))
    order_id = cursor.lastrowid
    for product_id, unit_price in selected:
        quantity = random.randint(1, 3)
        cursor.execute("""
            INSERT INTO order_items
            (order_id, product_id, quantity, unit_price)
            VALUES (%s, %s, %s, %s)
        """, (order_id, product_id,
              quantity, float(unit_price)))

conn.commit()
print("✅ Orders done!")

for table in ['customers','products','orders','order_items']:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"{table}: {cursor.fetchone()[0]} records")

cursor.close()
conn.close()
print("\n🎉 All data imported successfully!")