import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
import employee 


#test get staff by manager
class TestGetStaffByManager(unittest.TestCase):
    # Set up the Flask test client
    def setUp(self):
        employee.app.testing = True
        self.client = employee.app.test_client()

    @patch('employee.Employee')  # Mock the Employee model
    def test_get_staff_by_manager_success(self, mock_employee):
        # Mock the query result
        mock_employee.query.filter_by.return_value.all.return_value = [
            MagicMock(json=lambda: {
                "country": "Singapore",
                "dept": "Sales",
                "email": "Susan.Goh@allinone.com.sg",
                "position": "Account Manager",
                "reporting_manager": 140894,
                "role": 2,
                "staff_fname": "Susan",
                "staff_id": 140002,
                "staff_lname": "Goh"
            })
        ]

        # Make a GET request to the route
        response = self.client.get('/employee/get_staff/140894')

        # Define the expected response
        expected_response = {
            "code": 200,
            "data": [
                {
                    "country": "Singapore",
                    "dept": "Sales",
                    "email": "Susan.Goh@allinone.com.sg",
                    "position": "Account Manager",
                    "reporting_manager": 140894,
                    "role": 2,
                    "staff_fname": "Susan",
                    "staff_id": 140002,
                    "staff_lname": "Goh"
                }
            ]
        }

        # Assert the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected_response)

    @patch('employee.Employee')  # Mock the Employee model
    def test_get_staff_by_manager_not_found(self, mock_employee):
        # Simulate no employees reporting to the manager
        mock_employee.query.filter_by.return_value.all.return_value = []

        # Make a GET request to the route
        response = self.client.get('/employee/get_staff/999999')

        # Define the expected response
        expected_response = {
            "code": 404,
            "message": "No staff found reporting to manager with ID 999999."
        }

        # Assert the response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, expected_response)

    @patch('employee.Employee')  # Mock the Employee model
    def test_get_staff_by_manager_exception(self, mock_employee):
        # Simulate an exception during the query
        mock_employee.query.filter_by.side_effect = Exception("Database error")

        # Make a GET request to the route
        response = self.client.get('/employee/get_staff/140894')

        # Define the expected response
        expected_response = {
            "code": 500,
            "error": "An error occurred while fetching staff data. Database error"
        }

        # Assert the response
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, expected_response)




if __name__ == '__main__':
    unittest.main()
