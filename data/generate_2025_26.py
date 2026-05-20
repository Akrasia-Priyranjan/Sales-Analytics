import random
from datetime import datetime, timedelta
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="pri",  # apna password
    database="sales_db"
)
cursor = conn.cursor()

# Get existing customers
cursor.execute("SELECT customer_id FROM customers")
customer_ids = [row[0] for row in cursor.fetchall()]

# Get existing products
cursor.execute("SELECT product_id, price FROM products")
product_data = cursor.fetchall()

print(f"Customers: {len(customer_ids)}")
print(f"Products: {len(product_data)}")

statuses = [
    'delivered', 'delivered', 'delivered',
    'shipped', 'processing', 'cancelled'
]

# 2025 data
start_2025 = datetime(2025, 1, 1)
end_2025 = datetime(2025, 12, 31)

# 2026 data
start_2026 = datetime(2026, 1, 1)
end_2026 = datetime(2026, 6, 30)

def generate_orders(start_date, end_date, count):
    print(f"Inserting {count} orders from {start_date.year}...")
    for i in range(count):
        customer_id = random.choice(customer_ids)
        delta = end_date - start_date
        random_days = random.randint(0, delta.days)
        order_date = start_date + timedelta(days=random_days)
        status = random.choice(statuses)
        num_items = random.randint(1, 4)
        selected = random.sample(product_data, num_items)

        # Slight price increase for 2025-26
        total_amount = sum(
            float(price) * random.randint(1, 3) * 1.1
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
                  quantity, float(unit_price) * 1.1))

    conn.commit()
    print(f"✅ Done!")

# Generate data
generate_orders(start_2025, end_2025, 1200)  # 2025 - 1200 orders
generate_orders(start_2026, end_2026, 600)   # 2026 - 600 orders

# Verify
for table in ['orders', 'order_items']:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"{table}: {cursor.fetchone()[0]} records")

# Year wise
cursor.execute("""
    SELECT YEAR(order_date) as year, COUNT(*) as orders,
    SUM(total_amount) as revenue
    FROM orders
    GROUP BY year ORDER BY year
""")
print("\nYear wise data:")
for row in cursor.fetchall():
    print(f"Year {row[0]}: {row[1]} orders, ₹{row[2]:,.0f} revenue")

cursor.close()
conn.close()
print("\n🎉 2025-26 data added successfully!")