import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, json
import employee, view_requests, reject_requests, request_dates


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
                    {
                    "country": "Singapore",
                    "dept": "Engineering",
                    "email": "Eva.Ng@allinone.com.sg",
                    "position": "Junior Engineers",
                    "reporting_manager": 151408,
                    "role": 2,
                    "staff_fname": "Eva",
                    "staff_id": 150638,
                    "staff_lname": "Ng"
                    },
                    {
                    "country": "Singapore",
                    "dept": "Engineering",
                    "email": "Nanda.Kesavan@allinone.com.sg",
                    "position": "Junior Engineers",
                    "reporting_manager": 151408,
                    "role": 2,
                    "staff_fname": "Nanda",
                    "staff_id": 151591,
                    "staff_lname": "Kesavan"
                    },
                    {
                    "country": "Singapore",
                    "dept": "Engineering",
                    "email": "Ethan.Loh@allinone.com.sg",
                    "position": "Call Centre",
                    "reporting_manager": 151408,
                    "role": 2,
                    "staff_fname": "Ethan",
                    "staff_id": 150445,
                    "staff_lname": "Loh"
                    },
                ]
            },  # Staff list response
            {
                "data": [
                    {
                        "apply_reason": "Medical appointment",
                        "creation_date": "2024-09-13",
                        "reject_reason": None,
                        "request_id": 8,
                        "staff_id": 151591
                    },
                    {
                        "apply_reason": "Family event",
                        "creation_date": "2024-09-05",
                        "reject_reason": None,
                        "request_id": 5,
                        "staff_id": 150638
                    },
                    {
                        "apply_reason": "Medical appointment",
                        "creation_date": "2024-09-10",
                        "reject_reason": None,
                        "request_id": 2,
                        "staff_id": 150445
                    }
                ]
            },  # Staff requests response
            {"data": [
                {
                    "request_date": "2024-09-10",
                    "request_date_id": 4,
                    "request_id": 2,
                    "request_shift": "Full",
                    "request_status": "Pending Approval",
                    "rescind_reason": None,
                    "withdraw_reason": None
                },
                {
                    "request_date": "2024-09-17",
                    "request_date_id": 5,
                    "request_id": 2,
                    "request_shift": "Full",
                    "request_status": "Pending Approval",
                    "rescind_reason": None,
                    "withdraw_reason": None
                }
            ]},
            {"data": [
                {
                    "request_date": "2024-09-05",
                    "request_date_id": 8,
                    "request_id": 5,
                    "request_shift": "Full",
                    "request_status": "Pending Approval",
                    "rescind_reason": None,
                    "withdraw_reason": None
                }
            ]},
            {"data": [
                {
                    "request_date": "2024-09-13",
                    "request_date_id": 11,
                    "request_id": 8,
                    "request_shift": "Full",
                    "request_status": "Pending Approval",
                    "rescind_reason": None,
                    "withdraw_reason": None
                }
            ]}
        ]

        # Make a GET request to the endpoint
        response = self.client.get('/m_retrieve_requests/151408')

        # Assert that the response was successful
        self.assertEqual(response.status_code, 200)

        # Define the expected response
        expected_response = {
            "code": 200,
            "data": [
                {
                    "reason": "Medical appointment",
                    "request_dates": [
                        {
                            "2024-09-10": "PM"
                        }
                    ],
                    "request_id": 12,
                    "request_status": "Pending Approval",
                    "staff_id": 151408,
                    "staff_name": "Philip Lee"
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
        response = self.client.get('/m_retrieve_requests/150488')

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
        response = self.client.get('/m_retrieve_requests/140944')

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
        response = self.client.get('/m_retrieve_requests/999999')

        # Define the expected response for an error
        expected_response = {
            "code": 500,
            "error": "An error occurred while getting employee requests for manager staff_id 999999: Database error"
        }

        # Assert the response indicates an error
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, expected_response)


class TestRejectRequest(unittest.TestCase):
    def setUp(self):
        self.app = reject_requests.app.test_client()
        self.app.testing = True

    @patch("reject_requests.invoke_http")  # Correct path where it's used
    def test_reject_request_success(self, mock_invoke_http):
        # Mock responses for both API calls
        mock_invoke_http.side_effect = [
            {"code": 200, "message": "Reason updated successfully."},  # First call
            {"code": 200, "message": "Status updated successfully."},  # Second call
        ]

        # Simulate a PUT request to /reject_request
        request_data = {"request_id": 1, "reason": "Out of stock"}
        response = self.app.put("/reject_request", json=request_data)
        print(response)
        # Assert the response status code and message
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json["code"], 200)
        self.assertEqual(response_json["message"], "Request rejected successfully.")

    @patch("reject_requests.invoke_http")  # Same patching location
    def test_reject_request_failure(self, mock_invoke_http):
        # Mock the first API call to fail
        mock_invoke_http.side_effect = [
            {"code": 500, "message": "Failed to update reason."},  # First call fails
            {"code": 200, "message": "Status updated successfully."},  # Second call success
        ]

        # Simulate a PUT request to /reject_request
        request_data = {"request_id": 1, "reason": "Out of stock"}
        response = self.app.put("/reject_request", json=request_data)

        # Assert the response status code and message for failure
        self.assertEqual(response.status_code, 500)
        response_json = response.get_json()
        self.assertEqual(response_json["code"], 500)
        self.assertEqual(response_json["message"], "Failed to update reason.")

class ChangeAllStatusTestCase(unittest.TestCase):
    def setUp(self):
        # Setup the test client and app context
        self.app = request_dates.app.test_client()
        self.app.testing = True
        self.app_context = request_dates.app.app_context()
        self.app_context.push()

    def tearDown(self):
        # Tear down the app context after each test
        self.app_context.pop()

    @patch('request_dates.RequestDates')
    @patch('request_dates.db.session.commit')
    @patch('request_dates.invoke_http')
    def test_change_all_status(self, mock_invoke_http, mock_commit, MockRequestDates):
        # Sample request data
        request_data = {
            'request_id': 1,
            'status': 'Approved'
        }

        # Mock the database query to return a list of request dates
        mock_request_dates = MagicMock()
        MockRequestDates.query.filter_by.return_value.all.return_value = [mock_request_dates]
        
        # Mock the request date status
        mock_request_dates.request_status = "Pending"

        # Mock the response of the PUT request
        response = self.app.put('/request_dates/change_all_status', json=request_data)
        
        # Ensure the database query was called with the right arguments
        MockRequestDates.query.filter_by.assert_called_once_with(request_id=1)
        
        # Test the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('Request status for request ID 1 updated to Approved', response.get_data(as_text=True))

        # Ensure the commit and log invocation were called
        mock_commit.assert_called_once()
        mock_invoke_http.assert_called_once()

    @patch('request_dates.RequestDates')
    def test_change_all_status_missing_request_id_or_status(self, MockRequestDates):
        # Sample request data with missing 'request_id'
        request_data = {
            'status': 'Approved'
        }

        response = self.app.put('/request_dates/change_all_status', json=request_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Request ID or status not provided.', response.get_data(as_text=True))

    @patch('request_dates.RequestDates')
    def test_change_all_status_no_request_dates_found(self, MockRequestDates):
        # Sample request data
        request_data = {
            'request_id': 999,
            'status': 'Approved'
        }

        # Mocking the empty database response
        MockRequestDates.query.filter_by.return_value.all.return_value = []

        response = self.app.put('/request_dates/change_all_status', json=request_data)
        self.assertEqual(response.status_code, 404)
        self.assertIn('No request dates found for request ID 999', response.get_data(as_text=True))

    @patch('request_dates.RequestDates')
    @patch('request_dates.db.session.commit')
    @patch('request_dates.invoke_http')
    def test_change_all_status_exception(self, mock_invoke_http, mock_commit, MockRequestDates):
        # Mock a database query error
        MockRequestDates.query.filter_by.side_effect = Exception("Database error")

        request_data = {
            'request_id': 1,
            'status': 'Approved'
        }

        response = self.app.put('/request_dates/change_all_status', json=request_data)
        self.assertEqual(response.status_code, 500)
        self.assertIn('An error occurred while updating the request status', response.get_data(as_text=True))

    

if __name__ == '__main__':
    unittest.main()
