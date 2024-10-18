import unittest
from unittest.mock import patch, MagicMock
from pymongo import MongoClient
from database import Database  # Adjust this import based on your file structure

class TestDatabase(unittest.TestCase):
    @patch('pymongo.MongoClient', new_callable=MagicMock)
    def setUp(self, mock_mongo_client):
        # Mock the MongoClient to use mongomock
        self.database = Database()
        self.database.client = mock_mongo_client.return_value
        self.database.db = self.database.client['test_db']
        self.database.users = self.database.db['users']
        self.database.data = self.database.db['data']
        self.database.logs = self.database.db['logs']
        
    def test_add_user(self):
        user = {"username": "testuser", "email": "test@example.com"}
        result = self.database.add_user(user)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['username'], "testuser")

    def test_get_user(self):
        user = {"username": "testuser", "email": "test@example.com"}
        self.database.users.insert_one(user)
        
        result = self.database.get_user({"username": "testuser"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['username'], "testuser")

    def test_add_data(self):
        data = {"info": "test data"}
        result = self.database.add_data(data)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['info'], "test data")

    def test_get_all_data(self):
        data = {"info": "test data"}
        self.database.data.insert_one(data)
        
        result = self.database.get_all_data()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['info'], "test data")

    def test_update_data(self):
        data = {"info": "test data"}
        insert_result = self.database.data.insert_one(data)
        id = insert_result.inserted_id
        
        updated_data = {"info": "updated data"}
        result = self.database.update_data(str(id), updated_data)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['info'], "updated data")

    def test_delete_data(self):
        data = {"info": "test data"}
        insert_result = self.database.data.insert_one(data)
        id = insert_result.inserted_id
        
        result = self.database.delete_data(str(id))
        
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
