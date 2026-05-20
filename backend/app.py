from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from datetime import timedelta
from routes.auth import auth_bp
from routes.sales import sales_bp
from routes.analytics import analytics_bp
from routes.predict import predict_bp

app = Flask(__name__,
    template_folder='../frontend',
    static_folder='../frontend/static')

app.config['SECRET_KEY'] = 'sales_analytics_secret_2024'
app.config['JWT_SECRET_KEY'] = 'jwt_sales_secret_2024'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)

jwt = JWTManager(app)

app.register_blueprint(auth_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(predict_bp)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)