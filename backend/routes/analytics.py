from flask import Blueprint, jsonify, request
import mysql.connector
import pandas as pd

analytics_bp = Blueprint('analytics', __name__)

def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="pri",  # apna password
        database="sales_db"
    )

def get_filters():
    start = request.args.get('start', '2023-01-01')
    end = request.args.get('end', '2024-12-31')
    category = request.args.get('category', 'all')
    region = request.args.get('region', 'all')
    status = request.args.get('status', 'all')
    return start, end, category, region, status

@analytics_bp.route('/api/analytics/monthly', methods=['GET'])
def monthly_sales():
    start, end, category, region, status = get_filters()
    conn = get_conn()

    query = """
        SELECT
        DATE_FORMAT(o.order_date, '%Y-%m') as month,
        SUM(o.total_amount) as revenue,
        COUNT(DISTINCT o.order_id) as total_orders
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        JOIN categories cat ON p.category_id = cat.category_id
        WHERE o.order_date BETWEEN %s AND %s
    """
    params = [start, end]

    if category != 'all':
        query += " AND cat.category_name = %s"
        params.append(category)
    if region != 'all':
        query += " AND c.region = %s"
        params.append(region)
    if status != 'all':
        query += " AND o.status = %s"
        params.append(status)

    query += " GROUP BY month ORDER BY month"

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return jsonify(df.to_dict(orient='records'))


@analytics_bp.route('/api/analytics/top-products', methods=['GET'])
def top_products():
    start, end, category, region, status = get_filters()
    conn = get_conn()

    query = """
        SELECT
        p.product_name,
        SUM(oi.quantity) as units_sold,
        SUM(oi.quantity * oi.unit_price) as revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN categories cat ON p.category_id = cat.category_id
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_date BETWEEN %s AND %s
    """
    params = [start, end]

    if category != 'all':
        query += " AND cat.category_name = %s"
        params.append(category)
    if region != 'all':
        query += " AND c.region = %s"
        params.append(region)
    if status != 'all':
        query += " AND o.status = %s"
        params.append(status)

    query += """
        GROUP BY p.product_id, p.product_name
        ORDER BY revenue DESC
        LIMIT 10
    """

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return jsonify(df.to_dict(orient='records'))


@analytics_bp.route('/api/analytics/region', methods=['GET'])
def region_sales():
    start, end, category, region, status = get_filters()
    conn = get_conn()

    query = """
        SELECT
        c.region,
        COUNT(DISTINCT o.order_id) as orders,
        SUM(o.total_amount) as revenue
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        JOIN categories cat ON p.category_id = cat.category_id
        WHERE o.order_date BETWEEN %s AND %s
    """
    params = [start, end]

    if category != 'all':
        query += " AND cat.category_name = %s"
        params.append(category)
    if region != 'all':
        query += " AND c.region = %s"
        params.append(region)
    if status != 'all':
        query += " AND o.status = %s"
        params.append(status)

    query += " GROUP BY c.region ORDER BY revenue DESC"

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return jsonify(df.to_dict(orient='records'))


@analytics_bp.route('/api/analytics/category', methods=['GET'])
def category_sales():
    start, end, category, region, status = get_filters()
    conn = get_conn()

    query = """
        SELECT
        cat.category_name,
        SUM(oi.quantity * oi.unit_price) as revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN categories cat ON p.category_id = cat.category_id
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_date BETWEEN %s AND %s
    """
    params = [start, end]

    if category != 'all':
        query += " AND cat.category_name = %s"
        params.append(category)
    if region != 'all':
        query += " AND c.region = %s"
        params.append(region)
    if status != 'all':
        query += " AND o.status = %s"
        params.append(status)

    query += """
        GROUP BY cat.category_id, cat.category_name
        ORDER BY revenue DESC
    """

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return jsonify(df.to_dict(orient='records'))


@analytics_bp.route('/api/analytics/filters', methods=['GET'])
def get_filter_options():
    conn = get_conn()
    cats = pd.read_sql(
        "SELECT DISTINCT category_name FROM categories ORDER BY category_name",
        conn
    )
    regions = pd.read_sql(
        "SELECT DISTINCT region FROM customers ORDER BY region",
        conn
    )
    conn.close()
    return jsonify({
        'categories': cats['category_name'].tolist(),
        'regions': regions['region'].tolist(),
        'statuses': [
            'delivered', 'shipped',
            'processing', 'cancelled', 'pending'
        ]
    })
@analytics_bp.route('/api/analytics/customer-analytics', methods=['GET'])
def customer_analytics():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    # New vs Returning
    cursor.execute("""
SELECT
    SUM(CASE WHEN order_count = 1 THEN 1 ELSE 0 END) AS new_customers,
    SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) AS returning_customers
FROM (
    SELECT customer_id, COUNT(order_id) AS order_count
    FROM orders
    GROUP BY customer_id
) t
""")

    new_returning = cursor.fetchone()
    
    

    # Top Customers
    cursor.execute("""
        SELECT c.name, SUM(o.total_amount) AS total_spent
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.customer_id
        ORDER BY total_spent DESC
        LIMIT 5
    """)
    top_customers = cursor.fetchall()

    # Customer Growth
    cursor.execute("""
    SELECT
        DATE_FORMAT(order_date,'%Y-%m') AS month,
        COUNT(DISTINCT customer_id) AS customers
    FROM orders
    GROUP BY month
    ORDER BY month
""")
    growth = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "new_returning": new_returning,
        "top_customers": top_customers,
        "growth": growth
    })