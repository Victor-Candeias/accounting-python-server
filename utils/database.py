# Import necessary modules and libraries
# os: for accessing environment variables
# MongoClient: to connect to a MongoDB database
# ObjectId: to work with MongoDB document IDs
# load_dotenv: to load environment variables from a .env file
# logging: to log messages for debugging and monitoring
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
from utils.logging import logging
from utils import utilities

# Load environment variables from the .env file
load_dotenv()

class Database:
    """
    A singleton class to manage the connection to MongoDB and perform database operations.
    Ensures that only one instance of the database connection is created.
    """
    
    # Static property to hold the single instance of the class
    _instance = None

    def __new__(cls):
        """
        Override the default __new__ method to implement the singleton pattern.
        If an instance of the class doesn't exist, create and initialize it.
        """
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._init_db()  # Initialize the database connection
            
            logging.info('Initialize Database')  # Log that the database has been initialized
        
        return cls._instance

    def _init_db(self):
        """
        Initialize the database connection using the MongoDB URI and database name 
        from environment variables. Log the connection status and select the required collections.
        """
        
        # Load MongoDB connection string and database name from environment variables
        mongo_uri = os.getenv("MONGO_DB_CONNECTION_STRING")
        mongo_database = os.getenv("DATABASE_NAME")
        
        # Log the connection URI and database name for debugging
        logging.info(f"_init_db();mongo_uri={mongo_uri}")
        logging.info(f"_init_db();mongo_database={mongo_database}")
        
        # Establish connection to MongoDB
        self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Ping the database to check if the connection is successful
        self.client.admin.command('ping')
        is_connected = True  # Variable indicating successful connection
        logging.info("_init_db();MongoDB connected successfully.")
        
        # Select the database
        self.db = self.client[mongo_database]
        
        # References to collections within the database
        self.users = self.db["users"]
        self.data = self.db["data"]
        self.logs = self.db["logs"]

    # Add a user to the 'users' collection
    def add_user(self, user):
        """
        Insert a new user into the 'users' collection.
        
        Args:
            user (dict): The user data to be added.
        
        Returns:
            The result of the insert operation.
        """
        result = self.users.insert_one(user)
    
        # Insertion result log
        logging.info(f"add_user();inserted_id={result.inserted_id}")
        
        return result.inserted_id

    # Retrieve users from the 'users' collection based on a filter
    def get_user(self, filter={}):
        """
        Retrieve users from the 'users' collection that match the provided filter.
        
        Args:
            filter (dict): The filter criteria to match users (e.g., username).
        
        Returns:
            List of matching user documents.
        """
        logging.info(f"get_user();filter={filter}")
        
        result = list(self.users.find(filter))
        
        logging.info(f"get_user();1.result={result}")
        
        returnResult = None
        
        # Verifica se a lista resultante não está vazia
        if result:
            # Serializa os dados dos usuários encontrados
            returnResult = [self.serialize_data(user) for user in result]
        else:
            returnResult = []  # Retorna uma lista vazia se não encontrar usuários
        
        logging.info(f"get_user();returnResult={returnResult}")
        
        return returnResult

    # Add data to the 'data' collection
    def add_data(self, data):
        """
        Insert new data into the 'data' collection.
        
        Args:
            data (dict): The data to be added.
        
        Returns:
            The result of the insert operation.
        """
        logging.info(f"add_data();data={data}")
        
        result = self.data.insert_one(data)
        
        logging.info(f"add_data();all_data_serialized={result.inserted_id}")
        
        return result.inserted_id
    
    # Retrieve all data or filter specific records from the 'data' collection
    def get_all_data(self, filter={}):
        """
        Retrieve all data from the 'data' collection or use a filter to match specific records.
        
        Args:
            filter (dict): The filter criteria to match data records.
        
        Returns:
            List of matching data documents.
        """
        result = list(self.data.find(filter))
        
        logging.info(f"get_all_data();result={result}")
        
        all_data_serialized = [self.serialize_data(item) for item in result] if result else []
        
        logging.info(f"get_all_data();all_data_serialized={all_data_serialized}")
        
        return all_data_serialized

    # Update a specific data record by its ID
    def update_data(self, id, data):
        """
        Update an existing data record in the 'data' collection by its ID.
        
        Args:
            id (str): The ID of the data record to update.
            data (dict): The new data to update the record with.
        
        Returns:
            The updated data document.
        """
        result = self.data.find_one_and_update(
            {"_id": ObjectId(id)}, {"$set": data}, return_document=True
        )

        all_data_serialized = [self.serialize_data(item) for item in result] if result else []
        
        logging.info(f"update_data();all_data_serialized={all_data_serialized}")
        
        return all_data_serialized

    # Delete a specific data record by its ID
    def delete_data(self, id):
        """
        Delete a data record from the 'data' collection by its ID.
        
        Args:
            id (str): The ID of the data record to delete.
        
        Returns:
            The result of the delete operation.
        """
        result = self.data.delete_one({"_id": ObjectId(id)})
        
        all_data_serialized = [self.serialize_data(item) for item in result] if result else []
        
        logging.info(f"delete_data();all_data_serialized={all_data_serialized}")

        return all_data_serialized


    def serialize_data(self, data):
        """
        Converts MongoDB data into a JSON-serializable format.
        
        Args:
            data: The data to serialize, which can be of various types (ObjectId, dict, list).
        
        Returns:
            The JSON-serializable representation of the data.
        """
        if isinstance(data, ObjectId):
            return str(data)  # Convert ObjectId to string
        if isinstance(data, dict):
            return {key: self.serialize_data(value) for key, value in data.items()}  # Recursively serialize dictionary
        if isinstance(data, list):
            return [self.serialize_data(item) for item in data]  # Recursively serialize list
        return data  # Return the original data if no conversion is needed
    
    # Add a log entry to the 'logs' collection
    # def add_log(self, log):
    #     """
    #     Insert a new log entry into the 'logs' collection.
    #     
    #     Args:
    #         log (dict): The log data to be added.
        
    #     Returns:
    #         The result of the insert operation.
    #     """
    #     return self.logs.insert_one(log)

# Create a singleton instance of the Database class for use in the application
database = Database()
