import mysql.connector
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import pickle
import os

def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="pri",  # apna password
        database="sales_db"
    )

def train_and_save():
    conn = get_conn()

    # Get monthly revenue data
    df = pd.read_sql("""
        SELECT
        DATE_FORMAT(order_date, '%Y-%m') as month,
        SUM(total_amount) as revenue,
        COUNT(*) as orders
        FROM orders
        GROUP BY month
        ORDER BY month
    """, conn)
    conn.close()

    print("Training data:")
    print(df)

    # Prepare data
    df['month_num'] = range(1, len(df) + 1)

    X = df[['month_num']].values
    y_revenue = df['revenue'].values
    y_orders = df['orders'].values

    # Train models
    revenue_model = LinearRegression()
    revenue_model.fit(X, y_revenue)

    orders_model = LinearRegression()
    orders_model.fit(X, y_orders)

    # Save models
    os.makedirs('ml_model', exist_ok=True)

    with open('ml_model/revenue_model.pkl', 'wb') as f:
        pickle.dump(revenue_model, f)

    with open('ml_model/orders_model.pkl', 'wb') as f:
        pickle.dump(orders_model, f)

    # Save last month number
    with open('ml_model/last_month.pkl', 'wb') as f:
        pickle.dump({
            'last_month_num': len(df),
            'last_month': df['month'].iloc[-1],
            'months': df['month'].tolist()
        }, f)

    print("✅ Models trained and saved!")

    # Test predictions
    next_months = [[len(df) + 1], [len(df) + 2], [len(df) + 3]]
    rev_pred = revenue_model.predict(next_months)
    ord_pred = orders_model.predict(next_months)

    print("\nPredictions for next 3 months:")
    for i, (r, o) in enumerate(zip(rev_pred, ord_pred)):
        print(f"Month {i+1}: Revenue=₹{r:,.0f}, Orders={max(0,int(o))}")

if __name__ == '__main__':
    train_and_save()