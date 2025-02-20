from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
import re

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///C:/Users/balaj/db/mydb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
auth = HTTPBasicAuth()

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Added 'name' field

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name  # Return name in response
        }

# Create database tables before the first request
@app.before_request
def create_tables():
    db.create_all()

def validate_email(email):
    """Validate email format using regex."""
    return bool(EMAIL_REGEX.match(email))

# Verify user credentials for Basic Auth
@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        g.current_user = user
        return True
    return False

# Error handler for 404
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

# Error handler for 500
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# Registration endpoint
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        # Validate required fields
        required_fields = ['username', 'email', 'password', 'name']  # Added 'name' to required fields
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400

        # Check if username or email already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409

        # Create new user
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=hashed_password,
            name=data['name']  # Save the name field
        )
        
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'message': 'User registered successfully',
            'user': new_user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Login endpoint
@app.route('/login', methods=['GET'])
@auth.login_required
def login():
    return jsonify({
        'message': 'Login successful',
        'user': g.current_user.to_dict()
    }), 200

# Get all users
@app.route('/users', methods=['GET'])
@auth.login_required
def get_users():
    users = User.query.all()
    return jsonify({
        'users': [user.to_dict() for user in users]
    }), 200

# Get a single user by id
@app.route('/users/<int:user_id>', methods=['GET'])
@auth.login_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200

# Update a user's details
@app.route('/users/<int:user_id>', methods=['PUT'])
@auth.login_required
def update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        # Update username if provided
        if 'username' in data:
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': 'Username already taken'}), 409
            user.username = data['username']

        # Update email if provided
        if 'email' in data:
            if not validate_email(data['email']):
                return jsonify({'error': 'Invalid email format'}), 400
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': 'Email already taken'}), 409
            user.email = data['email']

        # Update password if provided
        if 'password' in data:
            user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

        # Update name if provided
        if 'name' in data:
            user.name = data['name']

        db.session.commit()
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete a user
@app.route('/users/<int:user_id>', methods=['DELETE'])
@auth.login_required
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
