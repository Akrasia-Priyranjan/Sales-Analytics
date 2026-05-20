from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
import bcrypt
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

users_db = {
    "admin": {
        "password": bcrypt.hashpw(b"admin123", bcrypt.gensalt()),
        "role": "admin",
        "name": "Admin User",
        "email": "admin@sales.com",
        "created": "2024-01-01"
    },
    "viewer": {
        "password": bcrypt.hashpw(b"viewer123", bcrypt.gensalt()),
        "role": "viewer",
        "name": "Viewer User",
        "email": "viewer@sales.com",
        "created": "2024-01-01"
    },
    "analyst": {
        "password": bcrypt.hashpw(b"analyst123", bcrypt.gensalt()),
        "role": "viewer",
        "name": "Data Analyst",
        "email": "analyst@sales.com",
        "created": "2024-01-01"
    }
}

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').encode('utf-8')

    if not username or not password:
        return jsonify({"error": "All fields required"}), 400

    if username in users_db:
        user = users_db[username]
        if bcrypt.checkpw(password, user['password']):
            access_token = create_access_token(
                identity=username,
                additional_claims={
                    "role": user['role'],
                    "name": user['name']
                },
                expires_delta=timedelta(hours=2)
            )
            return jsonify({
                "success": True,
                "token": access_token,
                "username": username,
                "role": user['role'],
                "name": user['name']
            })

    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/api/verify', methods=['GET'])
@jwt_required()
def verify():
    identity = get_jwt_identity()
    claims = get_jwt()
    return jsonify({
        "username": identity,
        "role": claims.get('role'),
        "name": claims.get('name'),
        "valid": True
    })

@auth_bp.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"error": "Admin only"}), 403

    users_list = []
    for uname, udata in users_db.items():
        users_list.append({
            "username": uname,
            "name": udata['name'],
            "email": udata['email'],
            "role": udata['role'],
            "created": udata['created']
        })
    return jsonify(users_list)

@auth_bp.route('/api/users/add', methods=['POST'])
@jwt_required()
def add_user():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"error": "Admin only"}), 403

    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    role = data.get('role', 'viewer')

    if not all([username, password, name, email]):
        return jsonify({"error": "All fields required"}), 400

    if username in users_db:
        return jsonify({"error": "User already exists"}), 400

    users_db[username] = {
        "password": bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt()
        ),
        "role": role,
        "name": name,
        "email": email,
        "created": "2025-01-01"
    }
    return jsonify({
        "success": True,
        "message": f"User {username} added!"
    })

@auth_bp.route('/api/users/delete', methods=['POST'])
@jwt_required()
def delete_user():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"error": "Admin only"}), 403

    data = request.json
    username = data.get('username')

    if username == 'admin':
        return jsonify({"error": "Cannot delete admin!"}), 400

    if username in users_db:
        del users_db[username]
        return jsonify({"success": True})

    return jsonify({"error": "User not found"}), 404

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    return jsonify({"success": True})