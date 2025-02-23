import os
import datetime
import boto3
import bcrypt
import jwt
from flask import Flask, request, jsonify

app = Flask(__name__)

# Environment configuration (set these in your Lambda environment)
USERS_TABLE = os.environ.get('USERS_TABLE', 'Users')
JWT_SECRET = "your_jwt_secret"#os.environ.get('JWT_SECRET', 'your_jwt_secret')
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600  # Token expires in 1 hour

# Initialize DynamoDB (ensure your region is correct)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
users_table = dynamodb.Table(USERS_TABLE)

@app.route('/')
def index():
    return 'Hello, AWS Lambda!'

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    # Check if user already exists
    try:
        response = users_table.get_item(Key={'username': username})
        if 'Item' in response:
            return jsonify({'error': 'User already exists'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Store the new user in DynamoDB
    try:
        users_table.put_item(
            Item={
                'username': username,
                'password': hashed_password.decode('utf-8')
            }
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    # Retrieve the user from DynamoDB
    try:
        response = users_table.get_item(Key={'username': username})
        if 'Item' not in response:
            return jsonify({'error': 'Invalid credentials'}), 400
        user = response['Item']
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    stored_password = user.get('password')
    if not bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
        return jsonify({'error': 'Invalid credentials'}), 400

    # Create JWT token with an expiration time
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return jsonify({'token': token}), 200

@app.route('/logout', methods=['POST'])
def logout():
    # With JWT, logout is usually handled client side by deleting the token.
    # For token revocation, you could implement a blacklist.
    return jsonify({'message': 'Logout successful'}), 200

if __name__ == '__main__':
    # For local testing only
    app.run(debug=True)
