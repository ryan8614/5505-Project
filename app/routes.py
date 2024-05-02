'''
Server routes implementation using Flask

'''

from flask import request, jsonify
from app import app

# Route for both login and registration
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    123
    """
    if request.method == 'POST':
        # Handle login POST request
        data = request.get_json()
        if data and "username" in data and "password" in data:
            # Here you would add your logic to verify the user credentials
            return jsonify({"status": "success", "message": "Logged in successfully"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid data"}), 400
    else:
        # Handle login GET request (optional, typically for forms or info)
        return 'Login Page'


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    456
    """
    if request.method == 'POST':
        # Handle registration POST request
        data = request.get_json()
        if data and "username" in data and "email" in data and "password" in data and "confirmPassword" in data:
            if data["password"] == data["confirmPassword"]:
                # Here you would add your logic to register the user
                return jsonify({"status": "success", "message": "Registered successfully"}), 200
            else:
                return jsonify({"status": "error", "message": "Passwords do not match"}), 400
        else:
            return jsonify({"status": "error", "message": "Invalid data"}), 400
    else:
        # Handle registration GET request (optional, typically for forms or info)
        return 'Registration Page'