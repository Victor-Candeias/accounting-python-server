# Import necessary libraries and modules 
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import bcrypt
import jwt

# Load environment variables from a .env file
from dotenv import load_dotenv

# Import custom utility functions and classes
# utilities: singleton instance providing common utilities
# database: singleton instance managing database connections and operations
# logging: singleton instance handling logging within the app
from utils import utilities
from utils.database import database
from utils.logging import logging
from flasgger import Swagger

# Load environment variables from the .env file into the app
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) for the Flask app
CORS(app)

# Secret key for JWT
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Initialize Swagger
swagger = Swagger(app)

# Define the route for user registration
# This endpoint will listen for POST requests at '/api/auth/register'
@app.route('/api/auth/register', methods=['POST'])
def register_user():
    """
    Handles user registration.
    ---
    tags:
      - Authentication
    parameters:
      - name: username
        in: body
        type: string
        required: true
        description: The username for registration
      - name: password
        in: body
        type: string
        required: true
        description: The password for registration
    responses:
      201:
        description: User registered successfully
      400:
        description: Username and password are required, or user already exists
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()  # Get JSON data from the request
        if not data or 'username' not in data or 'password' not in data:
          return jsonify({"error": "Invalid input"}), 400  # Return error if input is invalid

        username = data['username'].lower()
        password = data['password']

        logging.info(f"register_user();username={username}")
        
        if not utilities.validate_password_rules(password):
            return jsonify({"message": "Password does not meet complexity requirements"}), 400

        user_exists = database.get_user({'name': username})
        if user_exists:
            return jsonify({"message": "User already exists"}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        new_user = {'name': username, 'password': hashed_password}
        
        logging.info(f"register_user();new_user={new_user}")
        
        created_user = str(database.add_user(new_user))

        logging.info(f"register_user();created_user={created_user}")

        return jsonify({"message": "User registered successfully", "user": created_user}), 201
    
    except Exception as e:
        logging.error(f"register_user();Registration error: {e}")
        return jsonify({"message": "Internal server error"}), 500

# Define the route for user login
# This endpoint will listen for POST requests at '/api/auth/login'
@app.route('/api/auth/login', methods=['POST'])
def login_user():
    """
    Handles user login.
    ---
    tags:
      - Authentication
    parameters:
      - name: username
        in: body
        type: string
        required: true
        description: The username for login
      - name: password
        in: body
        type: string
        required: true
        description: The password for login
    responses:
      200:
        description: Successful login, returns JWT token
      400:
        description: Incorrect username or password
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()  # Get JSON data from the request
        if not data or 'username' not in data or 'password' not in data:
          return jsonify({"error": "Invalid input"}), 400  # Return error if input is invalid

        username = data['username'].lower()
        password = data['password']
    
        logging.info(f"login_user();username={username}")
        
        user = database.get_user({'name': username})
        if not user:
            return jsonify({"message": "User not found"}), 400

        logging.info(f"login_user();user={user}")

        password_bytes = password.encode('utf-8')
        encryptPassword = user[0]['password']
        
        logging.info(f"login_user();encryptPassword={encryptPassword}")
        
        passwordMatch = bcrypt.checkpw(password_bytes, encryptPassword)
        
        logging.info(f"login_user();passwordMatch={passwordMatch}")
        
        if not passwordMatch:
            return jsonify({"message": "Incorrect password"}), 400

        token = utilities.create_token(user)
        
        return jsonify({"token": token}), 200
    
    except Exception as e:
        logging.error(f"login_user();Login error: {e}")
        return jsonify({"message": "Internal server error"}), 500

# Define the route for retrieving data
# This endpoint will handle GET requests at '/api/data'
@app.route('/api/data', methods=['GET'])
def get_data():
    """
    Handles retrieval of data.
    ---
    tags:
      - Data
    parameters:
      - name: filter_data
        in: query
        type: object
        required: false
        description: Filters to be applied for fetching data
    responses:
      200:
        description: A list of data items
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
                description: The data ID
              content:
                type: string
                description: The content of the data item
      500:
        description: Internal server error
    """
    try:
        filter_data = request.args.to_dict()
        logging.info(f"get_data();filter_data={filter_data}")
        
        all_data = None
        
        # Fetch all data using the singleton instance (database)
        if not filter_data:
            all_data = database.get_all_data()  # Call method on the instance
        else:
            all_data = database.get_all_data(filter_data)  # Call method on the instance
            
        if not all_data:
            return jsonify([]), 200
        
        return jsonify(all_data), 200
    
    except Exception as e:
        logging.error(f"get_data();Error retrieving data: {e}")
        return jsonify({"message": "Error retrieving data"}), 500

# Define the route for adding data
# This endpoint will handle POST requests at '/api/data'
@app.route('/api/data', methods=['POST'])
def add_data():
    """
    Handles adding new data.
    ---
    tags:
      - Data
    parameters:
      - name: content
        in: body
        required: true
        schema:
          type: object
          properties:
            content:
              type: string
              description: The content to be added
        description: The JSON object containing the data to be added
    responses:
      201:
        description: Data added successfully
        schema:
          type: object
          properties:
            message:
              type: string
              description: Success message
            id:
              type: string
              description: The ID of the added data
      400:
        description: Content is required
      500:
        description: Internal server error
    """
    try:
        content = request.json.get('content', {})
        if not content:
            return jsonify({"message": "Content is required"}), 400

        logging.info(f"add_data()content={content}")
        
        new_data_id = str(database.add_data(content))  # Call method on the instance
        
        logging.info(f"add_data()new_data_id={new_data_id}")
        
        return jsonify({"message": "Data added", "id": new_data_id}), 201
    except Exception as e:
        logging.info(f"Error adding data: {e}")
        return jsonify({"message": "Error adding data"}), 500

# Define the route for deleting data by ID
# This endpoint will handle DELETE requests at '/api/data/<string:id>'
# The '<string:id>' is a route parameter used to identify the specific data to delete
@app.route('/api/data/<string:id>', methods=['DELETE'])
def delete_data(id):
    """
    Handles data deletion by ID.
    ---
    tags:
      - Data
    parameters:
      - name: id
        in: path
        type: string
        required: true
        description: The ID of the data to be deleted
    responses:
      204:
        description: Data deleted successfully (no content returned)
      404:
        description: Data not found
      500:
        description: Internal server error
    """
    try:
        logging.info(f"delete_data()id={id}")
        
        delete_result = database.delete_data(id)  # Call method on the instance
        if delete_result.deleted_count == 0:
            return jsonify({"message": "Data not found"}), 404

        return '', 204
    
    except Exception as e:
        print(f"Error deleting data: {e}")
        return jsonify({"message": "Error deleting data"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3001))
    app.run(host='0.0.0.0', port=port, debug=True)
