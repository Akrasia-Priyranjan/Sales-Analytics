from flask import Blueprint, jsonify, request
import mysql.connector
import pandas as pd

sales_bp = Blueprint('sales', __name__)

def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="pri",  # apna password
        database="sales_db"
    )

@sales_bp.route('/api/sales/all', methods=['GET'])
def get_all_sales():
    start = request.args.get('start', '2023-01-01')
    end = request.args.get('end', '2024-12-31')
    status = request.args.get('status', 'all')
    region = request.args.get('region', 'all')

    conn = get_conn()
    query = """
        SELECT o.order_id, c.name as customer,
        c.region, o.order_date,
        o.status, o.total_amount
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_date BETWEEN %s AND %s
    """
    params = [start, end]

    if status != 'all':
        query += " AND o.status = %s"
        params.append(status)
    if region != 'all':
        query += " AND c.region = %s"
        params.append(region)

    query += " ORDER BY o.order_date DESC"

    df = pd.read_sql(query, conn, params=params)
    df['order_date'] = df['order_date'].astype(str)
    return jsonify(df.to_dict(orient='records'))

@sales_bp.route('/api/sales/summary', methods=['GET'])
def sales_summary():
    start = request.args.get('start', '2023-01-01')
    end = request.args.get('end', '2024-12-31')
    status = request.args.get('status', 'all')
    region = request.args.get('region', 'all')

    conn = get_conn()
    query = """
        SELECT
        COUNT(*) as total_orders,
        SUM(o.total_amount) as total_revenue,
        AVG(o.total_amount) as avg_order_value
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_date BETWEEN %s AND %s
    """
    params = [start, end]

    if status != 'all':
        query += " AND o.status = %s"
        params.append(status)
    if region != 'all':
        query += " AND c.region = %s"
        params.append(region)

    df = pd.read_sql(query, conn, params=params)
    return jsonify(df.to_dict(orient='records')[0])