import unittest
from unittest.mock import patch, MagicMock
from flask import json
from app import app
import mongomock
from pymongo import MongoClient

class TestApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up the test client
        cls.client = app.test_client()
        cls.client.testing = True
        
        # Mock MongoDB connection
        cls.patched_client = patch('pymongo.MongoClient', new=mongomock.MongoClient)
        cls.patched_client.start()

    @classmethod
    def tearDownClass(cls):
        cls.patched_client.stop()

    @patch('utils.database.database')
    @patch('utils.utilities')
    def test_register_user(self, mock_utilities, mock_database):
        # Mock utility methods and database responses
        mock_utilities.validate_password_rules.return_value = True
        mock_database.get_user.return_value = None
        mock_database.add_user.return_value = {'inserted_id': 'mock_id'}

        # Simulate valid registration request
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps({'username': 'testuser', 'password': 'Password123'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], "User registered successfully")

        # Edge case: Empty request body
        response = self.client.post('/api/auth/register', data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "Username and password are required")

        # Edge case: Password does not meet complexity requirements
        mock_utilities.validate_password_rules.return_value = False
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps({'username': 'testuser', 'password': 'weakpass'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "Password does not meet complexity requirements")

    @patch('utils.database.database')
    @patch('utils.utilities')
    def test_login_user(self, mock_utilities, mock_database):
        # Mock valid user data and password hash
        mock_database.get_user.return_value = [{'name': 'testuser', 'password': 'hashed_password'}]
        mock_utilities.create_token.return_value = 'mocked_jwt_token'

        # Simulate valid login request
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({'username': 'testuser', 'password': 'Password123'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['token'], 'mocked_jwt_token')

        # Edge case: Empty request body
        response = self.client.post('/api/auth/login', data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "User not found")

        # Edge case: Incorrect password
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({'username': 'testuser', 'password': 'WrongPassword'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "Incorrect password")

    @patch('utils.database.database')
    def test_get_data(self, mock_database):
        # Mock valid data retrieval
        mock_database.get_all_data.return_value = [{'id': '1', 'content': 'Test data'}]

        # Simulate GET request to /api/data
        response = self.client.get('/api/data')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['content'], 'Test data')

        # Edge case: No data found (empty list)
        mock_database.get_all_data.return_value = []
        response = self.client.get('/api/data')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    @patch('utils.database.database')
    def test_add_data(self, mock_database):
        # Mock the database insertion to return a valid result
        mock_insert_result = MagicMock()
        mock_insert_result.inserted_id = 'mocked_id'
        mock_database.add_data.return_value = mock_insert_result

        mockData = {
            'description': 'description',
            'value': '1000',
            'entry': 'credit',
            'user': 'user',
            'day': '25',
            'month': 'november',
            'year': '2024',
        }
      
        # Simulate a valid POST request
        response = self.client.post(
            '/api/data',
            data=json.dumps({'content': mockData}),
            content_type='application/json'
        )
        
        # Assert that the response status code is 201 (Created)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], "Data added successfully")

    @patch('utils.database.database')
    def test_delete_data(self, mock_database):
        # Mock successful data deletion
        mock_database.delete_data.return_value = MagicMock(deleted_count=1)

        # Simulate valid DELETE request to /api/data/1
        response = self.client.delete('/api/data/1')
        self.assertEqual(response.status_code, 204)

        # Edge case: Data not found (deleted_count == 0)
        mock_database.delete_data.return_value = MagicMock(deleted_count=0)
        response = self.client.delete('/api/data/2')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], 'Data not found')

    @patch('utils.database.database')
    def test_internal_server_error(self, mock_database):
        # Simulate database exception
        mock_database.get_all_data.side_effect = Exception('Database error')

        # Simulate GET request to /api/data with an exception occurring
        response = self.client.get('/api/data')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json['message'], 'Error retrieving data')

if __name__ == '__main__':
    unittest.main()
