from flask import Blueprint, jsonify
import pickle
import os

predict_bp = Blueprint('predict', __name__)

# Model path fix
BASE_DIR = r"C:\Users\Asus\OneDrive\Desktop\sales-analytics"
MODEL_DIR = os.path.join(BASE_DIR, 'ml_model')

def load_models():
    try:
        rev_path = os.path.join(MODEL_DIR, 'revenue_model.pkl')
        ord_path = os.path.join(MODEL_DIR, 'orders_model.pkl')
        meta_path = os.path.join(MODEL_DIR, 'last_month.pkl')

        with open(rev_path, 'rb') as f:
            rev_model = pickle.load(f)
        with open(ord_path, 'rb') as f:
            ord_model = pickle.load(f)
        with open(meta_path, 'rb') as f:
            meta = pickle.load(f)

        return rev_model, ord_model, meta
    except Exception as e:
        print(f"Model load error: {e}")
        return None, None, None

@predict_bp.route('/api/predict/next-months', methods=['GET'])
def predict_next_months():
    rev_model, ord_model, meta = load_models()

    if rev_model is None:
        return jsonify({"error": "Model not trained yet"}), 400

    last_num = meta['last_month_num']
    last_month = meta['last_month']

    predictions = []
    year, month = map(int, last_month.split('-'))

    for i in range(1, 4):
        month += 1
        if month > 12:
            month = 1
            year += 1

        month_num = last_num + i
        rev = max(0, float(rev_model.predict([[month_num]])[0]))
        orders = max(0, int(ord_model.predict([[month_num]])[0]))

        predictions.append({
            'month': f"{year}-{month:02d}",
            'predicted_revenue': round(rev, 2),
            'predicted_orders': orders
        })

    return jsonify({
        'predictions': predictions,
        'model': 'Linear Regression',
        'based_on': f"{meta['last_month_num']} months of data"
    })

@predict_bp.route('/api/predict/trend', methods=['GET'])
def predict_trend():
    rev_model, ord_model, meta = load_models()

    if rev_model is None:
        return jsonify({"error": "Model not trained"}), 400

    coef = float(rev_model.coef_[0])

    if coef > 5000:
        trend = "📈 Strong Growth"
        color = "#34d399"
        advice = "Revenue growing strongly! Consider expanding inventory."
    elif coef > 0:
        trend = "📊 Steady Growth"
        color = "#818cf8"
        advice = "Steady growth observed. Maintain current strategy."
    else:
        trend = "📉 Declining"
        color = "#f87171"
        advice = "Revenue declining. Consider promotions or new products."

    return jsonify({
        'trend': trend,
        'color': color,
        'advice': advice,
        'monthly_growth': round(coef, 2)
    })