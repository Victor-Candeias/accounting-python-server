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
# /apidocs
swagger = Swagger(app)

# Define the route for user login
# @swagger
# POST /api/auth/login
# This endpoint is used for user login.
# It expects a JSON body with the following structure:
# {
#   "username": "user name",        # The username of the user (string)
#   "password": "user password"     # The password of the user (string)
# }
# The request method for this endpoint is POST.
@app.route('/api/auth/register', methods=['POST'])
def register_user():
    """
    Handles user login.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        description: JSON object containing username and password
        schema:
          type: object
          required:
            - username
            - password
            - role
          properties:
            username:
              type: string
              example: "user name"
            password:
              type: string
              example: "user password"
            role:
              type: string
              example: "user"
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
        if not data or 'username' not in data or 'password' not in data or 'role' not in data:
          return jsonify({"error": "Invalid input"}), 400  # Return error if input is invalid

        username = data['username'].lower()
        password = data['password']
        role = data['role']

        logging.info(f"register_user();username={username}")
        
        user_exists = database.get_user({'name': username})
        if user_exists:
            return jsonify({"message": "User already exists"}), 400

        # encrypt password
        hasedPassword = utilities.hash_password(password)

        new_user = {'username': username, 'password': hasedPassword, 'role': role}
        
        logging.info(f"register_user();new_user={str(new_user)}")
        
        created_user = str(database.add_user(new_user))

        logging.info(f"register_user();created_user={created_user}")

        return jsonify({"message": "User registered successfully", "user": created_user}), 201
    
    except Exception as e:
        logging.error(f"register_user();Registration error: {e}")
        return jsonify({"message": "Internal server error"}), 500

# Define the route for user registration
# @swagger
# POST /api/auth/register
# This endpoint is used for user registration.
# It expects a JSON body with the following structure:
# {
#   "username": "user name",        # The username of the user (string)
#   "password": "user password",     # The password of the user (string)
# }
# The request method for this endpoint is POST.
@app.route('/api/auth/login', methods=['POST'])
def login_user():
    """
    Handles user registration.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        description: JSON object containing user, password, and optional email
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "user name"
            password:
              type: string
              example: "user password"
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
    
        logging.info(f"login_user();username={username}")

        user = database.get_user({'username': username})
        if not user:
            return jsonify({"message": "User not found"}), 400

        logging.info(f"login_user();user={user}")

        encryptPassword = user[0]['password']
        
        passwordMatch = utilities.validate_password(encryptPassword, password)

        logging.info(f"login_user();passwordMatch={passwordMatch}")
        
        if not passwordMatch:
            return jsonify({"message": "Incorrect password"}), 400

        token = utilities.create_token(user)
        
        return jsonify({"token": token}), 200
    
    except Exception as e:
        logging.error(f"login_user();Login error: {e}")
        return jsonify({"message": "Internal server error"}), 500

# Define the route for retrieving data
# @swagger
# GET /api/data
# This endpoint retrieves data based on optional query parameters.
# Query parameters (optional):
#   - Any field (like "name", "type", etc.) to filter the data.
# Example request:
#   GET /api/data?name=value&age=30
# Response:
#   200 OK: Returns a JSON array of the filtered data.
#   500 Internal Server Error: If there is an error processing the request.
@app.route('/api/data', methods=['GET'])
def get_data():
    """
    Retrieves data based on optional filters.
    ---
    tags:
      - Data
    parameters:
      - name: filters
        in: query
        type: object
        description: Optional query parameters to filter data
        required: false
        schema:
          type: object
          additionalProperties:
            type: string
        example:
          username: "example_name"
          month: "09"
          year: "2024"
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

# Define the route for adding new data
# @swagger
# POST /api/data
# This endpoint allows adding new data to the database.
# The request body must contain a JSON object with the following structure:
# {
#   "content": "some content"  # The content to be added (string)
# }
# Example request:
#   POST /api/data
#   Body:
#   {
#     "content": "This is the content to be added."
#   }
# Responses:
#   201 Created: Data added successfully with a unique ID.
#   400 Bad Request: If the 'content' field is missing or empty.
#   500 Internal Server Error: If an error occurs while adding data.
@app.route('/api/data', methods=['POST'])
def add_data():
    """
    Handles adding new data.
    ---
    tags:
      - Data
    parameters:
      - in: body
        name: body
        description: JSON object containing the data to be added
        schema:
          type: object
          required:
            - content
          properties:
            content:
              type: string
              description: The content to be added
              example: "This is some content to add"
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
        schema:
          type: object
          properties:
            message:
              type: string
              description: Error message
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            message:
              type: string
              description: Error message
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
# @swagger
# DELETE /api/data/{id}
# This endpoint deletes data by its unique ID.
# Path Parameter:
#   - id: The ID of the data to be deleted (string).
# Example request:
#   DELETE /api/data/12345
# Responses:
#   204 No Content: Data deleted successfully, no content returned.
#   404 Not Found: If the data with the given ID does not exist.
#   500 Internal Server Error: If an error occurs while processing the request.
@app.route('/api/data/<string:id>', methods=['DELETE'])
def delete_data(id):
    """
    Deletes data by ID.
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
        schema:
          type: object
          properties:
            message:
              type: string
              description: Error message
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            message:
              type: string
              description: Error message
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
