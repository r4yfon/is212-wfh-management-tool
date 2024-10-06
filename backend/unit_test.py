import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
import employee, view_requests


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

import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
import view_requests

class TestMRetrieveRequests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True
        self.client = view_requests.app.test_client()

    @patch('view_requests.invoke_http')  # Mock the invoke_http method
    def test_m_retrieve_requests_success(self, mock_invoke_http):
        # Mock responses for the sequence of invoke_http calls
        mock_invoke_http.side_effect = [
            {
                "data": [
                    {"staff_id": 150488, "staff_fname": "Jacob", "staff_lname": "Tan"}
                ]
            },  # Staff list response
            {
                "data": [
                    {"request_id": 1, "staff_id": 150488, "apply_reason": "Family event"},
                    {"request_id": 2, "staff_id": 150488, "apply_reason": "Medical appointment"}
                ]
            },  # Staff requests response
            [
                {"data": [{"request_date": "2024-05-29", "request_status": "Pending Approval"}]},  # Request dates response for request_id 1
                {"data": [{"request_date": "2024-09-12", "request_status": "Pending Withdrawal"}]}  # Request dates response for request_id 2
            ]
        ]

        # Make a GET request to the endpoint
        response = self.client.get('/m_retrieve_requests')

        # Assert that the response was successful
        self.assertEqual(response.status_code, 200)

        # Define the expected response
        expected_response = {
            "code": 200,
            "data": [
                {
                    "reason": "Family event",
                    "request_dates": ["2024-05-29"],
                    "request_id": 1,
                    "request_status": "Pending Approval",
                    "staff_id": 150488,
                    "staff_name": "Jacob Tan"
                },
                {
                    "reason": "Medical appointment",
                    "request_dates": ["2024-09-12"],
                    "request_id": 2,
                    "request_status": "Pending Withdrawal",
                    "staff_id": 150488,
                    "staff_name": "Jacob Tan"
                }
            ]
        }
        self.assertEqual(response.json, expected_response)

    @patch('view_requests.invoke_http')  # Mock the invoke_http method
    def test_m_retrieve_requests_no_staff(self, mock_invoke_http):
        # Mock responses when no staff are returned
        mock_invoke_http.side_effect = [
            {"data": []},  # No staff
            {"data": []},  # No requests
        ]

        # Make a GET request to the endpoint
        response = self.client.get('/m_retrieve_requests')

        # Assert that the response was successful with an empty data list
        self.assertEqual(response.status_code, 200)
        expected_response = {
            "code": 200,
            "data": []
        }
        self.assertEqual(response.json, expected_response)

    @patch('view_requests.invoke_http')  # Mock the invoke_http method
    def test_m_retrieve_requests_no_requests(self, mock_invoke_http):
        # Mock responses with staff but no requests
        mock_invoke_http.side_effect = [
            {
                "data": [
                    {"staff_id": 150488, "staff_fname": "Jacob", "staff_lname": "Tan"}
                ]
            },  # Staff list response
            {
                "data": []  # No requests
            }
        ]

        # Make a GET request to the endpoint
        response = self.client.get('/m_retrieve_requests')

        # Assert that the response was successful with an empty data list
        self.assertEqual(response.status_code, 200)
        expected_response = {
            "code": 200,
            "data": []
        }
        self.assertEqual(response.json, expected_response)

    @patch('view_requests.invoke_http')  # Mock the invoke_http method
    def test_m_retrieve_requests_exception(self, mock_invoke_http):
        # Simulate an exception during the invoke_http call
        mock_invoke_http.side_effect = Exception("Database error")

        # Make a GET request to the endpoint
        response = self.client.get('/m_retrieve_requests')

        # Define the expected response for an error
        expected_response = {
            "code": 500,
            "error": "An error occurred while getting employee requests for manager staff_id 130002: Database error"
        }

        # Assert the response indicates an error
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, expected_response)

if __name__ == '__main__':
    unittest.main()
