import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, json
import employee, view_requests, reject_requests, request_dates
import unittest
import flask_testing
from request_dates import app as request_dates_app, db, RequestDates
from employee import db as employee_db, Employee
from request import db as request_db, Request
from request_dates import db as request_dates_db, RequestDates
from status_log import db as status_log_db, StatusLog
from datetime import date
from flask import jsonify
from reject_requests import app as reject_requests_app, invoke_http
import datetime
from view_requests import app as view_requests_app


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
            "error": "An error occurred: Database error"
        }

        # Assert the response
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, expected_response)

class TestMRetrieveRequests(unittest.TestCase):
    def setUp(self):
        # Use the actual Flask application
        self.app = view_requests_app
        self.app.testing = True
        self.client = self.app.test_client()
        self.maxDiff = None

    @patch('view_requests.invoke_http')  # Mock the invoke_http method
    def test_m_retrieve_requests_success(self, mock_invoke_http):
        # Mock responses for the sequence of invoke_http calls
        mock_invoke_http.return_value = [
            {
                "staff_id": 150488,
                "staff_fname": "Jacob",
                "staff_lname": "Tan",
                "request_id": 1,
                "creation_date": datetime.date(2024, 10, 17),
                "apply_reason": "Family event",
                "reject_reason": None,
                "request_date_id": 1,
                "request_date": datetime.date(2024, 10, 22),
                "request_shift": "PM",
                "request_status": "Pending Approval",
                "rescind_reason": None,
                "withdraw_reason": None
            },
            {
                "staff_id": 150446,
                "staff_fname": "Daniel",
                "staff_lname": "Tan",
                "request_id": 2,
                "creation_date": datetime.date(2024, 10, 22),
                "apply_reason": "Medical appointment",
                "reject_reason": None,
                "request_date_id": 3,
                "request_date": datetime.date(2024, 10, 10),
                "request_shift": "Full",
                "request_status": "Pending Approval",
                "rescind_reason": None,
                "withdraw_reason": None
            }
        ]

        # Make a GET request to the endpoint
        response = self.client.get('/m_retrieve_requests/151408')

        # Assert that the response was successful
        self.assertEqual(response.status_code, 200)

        # Define the expected response
        expected_response = {'code': 200, 'data': [{'apply_reason': 'Family event', 'creation_date': '2024-09-15', 'reject_reason': None, 'request_id': 1, 'staff_id': 150488, 'staff_name': 'Jacob Tan', 'wfh_dates': [{'request_date': '2024-09-15', 'request_date_id': 1, 'request_shift': 'PM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}, {'request_date': '2024-09-22', 'request_date_id': 2, 'request_shift': 'PM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}, {'request_date': '2024-09-29', 'request_date_id': 3, 'request_shift': 'PM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Medical appointment', 'creation_date': '2024-09-10', 'reject_reason': None, 'request_id': 2, 'staff_id': 150488, 'staff_name': 'Jacob Tan', 'wfh_dates': [{'request_date': '2024-09-10', 'request_date_id': 4, 'request_shift': 'Full', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}, {'request_date': '2024-09-17', 'request_date_id': 5, 'request_shift': 'Full', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Personal reasons', 'creation_date': '2024-09-12', 'reject_reason': 'Insufficient documentation', 'request_id': 3, 'staff_id': 150446, 'staff_name': 'Daniel Tan', 'wfh_dates': [{'request_date': '2024-09-12', 'request_date_id': 6, 'request_shift': 'AM', 'request_status': 'Rejected', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Vacation', 'creation_date': '2024-09-11', 'reject_reason': None, 'request_id': 4, 'staff_id': 150632, 'staff_name': 'Charlotte Toh', 'wfh_dates': [{'request_date': '2024-09-11', 'request_date_id': 7, 'request_shift': 'Full', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Family event', 'creation_date': '2024-09-05', 'reject_reason': None, 'request_id': 5, 'staff_id': 150638, 'staff_name': 'Eva Ng', 'wfh_dates': [{'request_date': '2024-09-05', 'request_date_id': 8, 'request_shift': 'Full', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Conference', 'creation_date': '2024-09-18', 'reject_reason': None, 'request_id': 6, 'staff_id': 150645, 'staff_name': 'Sophia Tan', 'wfh_dates': [{'request_date': '2024-09-18', 'request_date_id': 9, 'request_shift': 'Full', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Personal reasons', 'creation_date': '2024-09-14', 'reject_reason': 'Not enough staff coverage', 'request_id': 7, 'staff_id': 151595, 'staff_name': 'Mani Devi', 'wfh_dates': [{'request_date': '2024-09-14', 'request_date_id': 10, 'request_shift': 'Full', 'request_status': 'Rejected', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Medical appointment', 'creation_date': '2024-09-13', 'reject_reason': None, 'request_id': 8, 'staff_id': 151591, 'staff_name': 'Nanda Kesavan', 'wfh_dates': [{'request_date': '2024-09-13', 'request_date_id': 11, 'request_shift': 'Full', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Family event', 'creation_date': '2024-09-17', 'reject_reason': None, 'request_id': 9, 'staff_id': 151596, 'staff_name': 'Koh Seng', 'wfh_dates': [{'request_date': '2024-09-17', 'request_date_id': 12, 'request_shift': 'PM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Vacation', 'creation_date': '2024-09-16', 'reject_reason': 'Project deadline', 'request_id': 10, 'staff_id': 151598, 'staff_name': 'Kumaru Pillai', 'wfh_dates': [{'request_date': '2024-09-16', 'request_date_id': 13, 'request_shift': 'Full', 'request_status': 'Rejected', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Family event', 'creation_date': '2024-10-15', 'reject_reason': None, 'request_id': 11, 'staff_id': 150488, 'staff_name': 'Jacob Tan', 'wfh_dates': [{'request_date': '2024-10-15', 'request_date_id': 14, 'request_shift': 'PM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Family event', 'creation_date': '2024-10-13', 'reject_reason': None, 'request_id': 12, 'staff_id': 150488, 'staff_name': 'Jacob Tan', 'wfh_dates': [{'request_date': '2024-10-13', 'request_date_id': 15, 'request_shift': 'PM', 'request_status': 'Rejected', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Feeling Sick', 'creation_date': '2024-06-13', 'reject_reason': None, 'request_id': 13, 'staff_id': 150488, 'staff_name': 'Jacob Tan', 'wfh_dates': [{'request_date': '2024-07-11', 'request_date_id': 16, 'request_shift': 'PM', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Feeling Sick', 'creation_date': '2024-10-13', 'reject_reason': None, 'request_id': 15, 'staff_id': 150488, 'staff_name': 'Jacob Tan', 'wfh_dates': [{'request_date': '2024-10-13', 'request_date_id': 18, 'request_shift': 'AM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}, {'request_date': '2024-10-14', 'request_date_id': 19, 'request_shift': 'AM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Vacation', 'creation_date': '2024-09-24', 'reject_reason': 'Project deadline', 'request_id': 25, 'staff_id': 150488, 'staff_name': 'Jacob Tan', 'wfh_dates': [{'request_date': '2024-10-09', 'request_date_id': 29, 'request_shift': 'AM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Family gathering', 'creation_date': '2024-09-25', 'reject_reason': None, 'request_id': 26, 'staff_id': 150446, 'staff_name': 'Daniel Tan', 'wfh_dates': [{'request_date': '2024-10-10', 'request_date_id': 30, 'request_shift': 'PM', 'request_status': 'Rejected', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Birthday', 'creation_date': '2024-09-26', 'reject_reason': None, 'request_id': 27, 'staff_id': 150632, 'staff_name': 'Charlotte Toh', 'wfh_dates': [{'request_date': '2024-10-11', 'request_date_id': 31, 'request_shift': 'Full', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Personal reasons', 'creation_date': '2024-09-27', 'reject_reason': 'Insufficient documentation', 'request_id': 28, 'staff_id': 150638, 'staff_name': 'Eva Ng', 'wfh_dates': [{'request_date': '2024-10-12', 'request_date_id': 32, 'request_shift': 'AM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Vacation', 'creation_date': '2024-09-28', 'reject_reason': None, 'request_id': 29, 'staff_id': 150645, 'staff_name': 'Sophia Tan', 'wfh_dates': [{'request_date': '2024-10-13', 'request_date_id': 33, 'request_shift': 'PM', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Family event', 'creation_date': '2024-09-29', 'reject_reason': None, 'request_id': 30, 'staff_id': 151595, 'staff_name': 'Mani Devi', 'wfh_dates': [{'request_date': '2024-10-14', 'request_date_id': 34, 'request_shift': 'Full', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Conference', 'creation_date': '2024-09-30', 'reject_reason': None, 'request_id': 31, 'staff_id': 151591, 'staff_name': 'Nanda Kesavan', 'wfh_dates': [{'request_date': '2024-10-15', 'request_date_id': 35, 'request_shift': 'AM', 'request_status': 'Rejected', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Personal reasons', 'creation_date': '2024-10-01', 'reject_reason': 'Not enough staff coverage', 'request_id': 32, 'staff_id': 151596, 'staff_name': 'Koh Seng', 'wfh_dates': [{'request_date': '2024-10-16', 'request_date_id': 36, 'request_shift': 'PM', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Medical appointment', 'creation_date': '2024-10-02', 'reject_reason': None, 'request_id': 33, 'staff_id': 151598, 'staff_name': 'Kumaru Pillai', 'wfh_dates': [{'request_date': '2024-10-17', 'request_date_id': 37, 'request_shift': 'Full', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Personal reasons', 'creation_date': '2024-10-11', 'reject_reason': 'Not enough staff coverage', 'request_id': 42, 'staff_id': 150488, 'staff_name': 'Jacob Tan', 'wfh_dates': [{'request_date': '2024-10-27', 'request_date_id': 47, 'request_shift': 'Full', 'request_status': 'Rejected', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Medical appointment', 'creation_date': '2024-10-12', 'reject_reason': None, 'request_id': 43, 'staff_id': 150446, 'staff_name': 'Daniel Tan', 'wfh_dates': [{'request_date': '2024-10-28', 'request_date_id': 48, 'request_shift': 'AM', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}, {'request_date': '2024-10-29', 'request_date_id': 49, 'request_shift': 'PM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Family event', 'creation_date': '2024-10-13', 'reject_reason': None, 'request_id': 44, 'staff_id': 150632, 'staff_name': 'Charlotte Toh', 'wfh_dates': [{'request_date': '2024-10-30', 'request_date_id': 50, 'request_shift': 'Full', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Vacation', 'creation_date': '2024-10-14', 'reject_reason': 'Project deadline', 'request_id': 45, 'staff_id': 150638, 'staff_name': 'Eva Ng', 'wfh_dates': [{'request_date': '2024-10-31', 'request_date_id': 51, 'request_shift': 'AM', 'request_status': 'Rejected', 'rescind_reason': None, 'withdraw_reason': None}, {'request_date': '2024-11-01', 'request_date_id': 52, 'request_shift': 'PM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Family gathering', 'creation_date': '2024-10-15', 'reject_reason': None, 'request_id': 46, 'staff_id': 150645, 'staff_name': 'Sophia Tan', 'wfh_dates': [{'request_date': '2024-11-02', 'request_date_id': 53, 'request_shift': 'Full', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Birthday', 'creation_date': '2024-10-16', 'reject_reason': None, 'request_id': 47, 'staff_id': 151595, 'staff_name': 'Mani Devi', 'wfh_dates': [{'request_date': '2024-11-03', 'request_date_id': 54, 'request_shift': 'AM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}, {'request_date': '2024-11-04', 'request_date_id': 55, 'request_shift': 'PM', 'request_status': 'Rejected', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Personal reasons', 'creation_date': '2024-10-17', 'reject_reason': 'Insufficient documentation', 'request_id': 48, 'staff_id': 151591, 'staff_name': 'Nanda Kesavan', 'wfh_dates': [{'request_date': '2024-11-05', 'request_date_id': 56, 'request_shift': 'Full', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Vacation', 'creation_date': '2024-10-18', 'reject_reason': None, 'request_id': 49, 'staff_id': 151596, 'staff_name': 'Koh Seng', 'wfh_dates': [{'request_date': '2024-11-06', 'request_date_id': 57, 'request_shift': 'AM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}, {'request_date': '2024-11-07', 'request_date_id': 58, 'request_shift': 'PM', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Family event', 'creation_date': '2024-10-19', 'reject_reason': None, 'request_id': 50, 'staff_id': 151598, 'staff_name': 'Kumaru Pillai', 'wfh_dates': [{'request_date': '2024-11-08', 'request_date_id': 59, 'request_shift': 'Full', 'request_status': 'Rejected', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Vacation', 'creation_date': '2024-10-28', 'reject_reason': None, 'request_id': 59, 'staff_id': 150488, 'staff_name': 'Jacob Tan', 'wfh_dates': [{'request_date': '2024-11-21', 'request_date_id': 72, 'request_shift': 'AM', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Family event', 'creation_date': '2024-10-29', 'reject_reason': None, 'request_id': 60, 'staff_id': 150446, 'staff_name': 'Daniel Tan', 'wfh_dates': [{'request_date': '2024-11-22', 'request_date_id': 73, 'request_shift': 'PM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Conference', 'creation_date': '2024-10-30', 'reject_reason': None, 'request_id': 61, 'staff_id': 150632, 'staff_name': 'Charlotte Toh', 'wfh_dates': [{'request_date': '2024-11-23', 'request_date_id': 74, 'request_shift': 'Full', 'request_status': 'Rejected', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Personal reasons', 'creation_date': '2024-10-31', 'reject_reason': 'Not enough staff coverage', 'request_id': 62, 'staff_id': 150638, 'staff_name': 'Eva Ng', 'wfh_dates': [{'request_date': '2024-11-24', 'request_date_id': 75, 'request_shift': 'AM', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Medical appointment', 'creation_date': '2024-11-01', 'reject_reason': None, 'request_id': 63, 'staff_id': 150645, 'staff_name': 'Sophia Tan', 'wfh_dates': [{'request_date': '2024-11-25', 'request_date_id': 76, 'request_shift': 'PM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Family event', 'creation_date': '2024-11-02', 'reject_reason': None, 'request_id': 64, 'staff_id': 151595, 'staff_name': 'Mani Devi', 'wfh_dates': [{'request_date': '2024-11-26', 'request_date_id': 77, 'request_shift': 'Full', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Vacation', 'creation_date': '2024-11-03', 'reject_reason': 'Project deadline', 'request_id': 65, 'staff_id': 151591, 'staff_name': 'Nanda Kesavan', 'wfh_dates': [{'request_date': '2024-11-27', 'request_date_id': 78, 'request_shift': 'AM', 'request_status': 'Rejected', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Family gathering', 'creation_date': '2024-11-04', 'reject_reason': None, 'request_id': 66, 'staff_id': 151596, 'staff_name': 'Koh Seng', 'wfh_dates': [{'request_date': '2024-11-28', 'request_date_id': 79, 'request_shift': 'PM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Birthday', 'creation_date': '2024-11-05', 'reject_reason': None, 'request_id': 67, 'staff_id': 151598, 'staff_name': 'Kumaru Pillai', 'wfh_dates': [{'request_date': '2024-11-29', 'request_date_id': 80, 'request_shift': 'Full', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Vacation', 'creation_date': '2024-11-14', 'reject_reason': None, 'request_id': 76, 'staff_id': 150488, 'staff_name': 'Jacob Tan', 'wfh_dates': [{'request_date': '2024-12-08', 'request_date_id': 89, 'request_shift': 'Full', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Family event', 'creation_date': '2024-11-15', 'reject_reason': None, 'request_id': 77, 'staff_id': 150446, 'staff_name': 'Daniel Tan', 'wfh_dates': [{'request_date': '2024-12-09', 'request_date_id': 90, 'request_shift': 'AM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Conference', 'creation_date': '2024-11-16', 'reject_reason': None, 'request_id': 78, 'staff_id': 150632, 'staff_name': 'Charlotte Toh', 'wfh_dates': [{'request_date': '2024-12-10', 'request_date_id': 91, 'request_shift': 'PM', 'request_status': 'Rejected', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Personal reasons', 'creation_date': '2024-11-17', 'reject_reason': 'Not enough staff coverage', 'request_id': 79, 'staff_id': 150638, 'staff_name': 'Eva Ng', 'wfh_dates': [{'request_date': '2024-12-11', 'request_date_id': 92, 'request_shift': 'Full', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Medical appointment', 'creation_date': '2024-11-18', 'reject_reason': None, 'request_id': 80, 'staff_id': 150645, 'staff_name': 'Sophia Tan', 'wfh_dates': [{'request_date': '2024-12-12', 'request_date_id': 93, 'request_shift': 'AM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Family event', 'creation_date': '2024-11-19', 'reject_reason': None, 'request_id': 81, 'staff_id': 151595, 'staff_name': 'Mani Devi', 'wfh_dates': [{'request_date': '2024-12-13', 'request_date_id': 94, 'request_shift': 'PM', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Vacation', 'creation_date': '2024-11-20', 'reject_reason': 'Project deadline', 'request_id': 82, 'staff_id': 151591, 'staff_name': 'Nanda Kesavan', 'wfh_dates': [{'request_date': '2024-12-14', 'request_date_id': 95, 'request_shift': 'Full', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Family gathering', 'creation_date': '2024-11-21', 'reject_reason': None, 'request_id': 83, 'staff_id': 151596, 'staff_name': 'Koh Seng', 'wfh_dates': [{'request_date': '2024-12-15', 'request_date_id': 96, 'request_shift': 'AM', 'request_status': 'Rejected', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Birthday', 'creation_date': '2024-11-22', 'reject_reason': None, 'request_id': 84, 'staff_id': 151598, 'staff_name': 'Kumaru Pillai', 'wfh_dates': [{'request_date': '2024-12-16', 'request_date_id': 97, 'request_shift': 'PM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Vacation', 'creation_date': '2024-12-01', 'reject_reason': 'Project deadline', 'request_id': 93, 'staff_id': 150488, 'staff_name': 'Jacob Tan', 'wfh_dates': [{'request_date': '2024-12-26', 'request_date_id': 107, 'request_shift': 'Full', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Family event', 'creation_date': '2024-12-02', 'reject_reason': None, 'request_id': 94, 'staff_id': 150446, 'staff_name': 'Daniel Tan', 'wfh_dates': [{'request_date': '2024-12-27', 'request_date_id': 108, 'request_shift': 'AM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}, {'request_date': '2024-12-28', 'request_date_id': 109, 'request_shift': 'PM', 'request_status': 'Denied', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Conference', 'creation_date': '2024-12-03', 'reject_reason': None, 'request_id': 95, 'staff_id': 150632, 'staff_name': 'Charlotte Toh', 'wfh_dates': [{'request_date': '2024-12-29', 'request_date_id': 110, 'request_shift': 'Full', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Personal reasons', 'creation_date': '2024-12-04', 'reject_reason': 'Insufficient documentation', 'request_id': 96, 'staff_id': 150638, 'staff_name': 'Eva Ng', 'wfh_dates': [{'request_date': '2024-12-30', 'request_date_id': 111, 'request_shift': 'AM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Medical appointment', 'creation_date': '2024-12-05', 'reject_reason': None, 'request_id': 97, 'staff_id': 150645, 'staff_name': 'Sophia Tan', 'wfh_dates': [{'request_date': '2024-12-31', 'request_date_id': 112, 'request_shift': 'PM', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Family event', 'creation_date': '2024-12-06', 'reject_reason': None, 'request_id': 98, 'staff_id': 151595, 'staff_name': 'Mani Devi', 'wfh_dates': [{'request_date': '2025-01-01', 'request_date_id': 113, 'request_shift': 'Full', 'request_status': 'Denied', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Vacation', 'creation_date': '2024-12-07', 'reject_reason': None, 'request_id': 99, 'staff_id': 151591, 'staff_name': 'Nanda Kesavan', 'wfh_dates': [{'request_date': '2025-01-02', 'request_date_id': 114, 'request_shift': 'AM', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Family gathering', 'creation_date': '2024-12-08', 'reject_reason': None, 'request_id': 100, 'staff_id': 151596, 'staff_name': 'Koh Seng', 'wfh_dates': [{'request_date': '2025-01-03', 'request_date_id': 115, 'request_shift': 'PM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, {'apply_reason': 'Birthday', 'creation_date': '2024-12-09', 'reject_reason': None, 'request_id': 101, 'staff_id': 151598, 'staff_name': 'Kumaru Pillai', 'wfh_dates': [{'request_date': '2025-01-04', 'request_date_id': 116, 'request_shift': 'Full', 'request_status': 'Pending Approval', 'rescind_reason': None, 'withdraw_reason': None}]}]}

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
        response = self.client.get('/m_retrieve_requests/')

        # Assert the response indicates an error
        self.assertEqual(response.status_code, 404)

class TestRejectRequest(unittest.TestCase):
    def setUp(self):
        self.app = reject_requests.app.test_client()
        self.app.testing = True

    @patch('reject_requests.invoke_http')  # Mock the invoke_http function
    def test_reject_request_success(self, mock_invoke_http):
        # Simulate the behavior of external services using MagicMock

        # Mocking the /update_reason API call to return a success response
        mock_invoke_http.side_effect = [
            {"code": 200, "message": "Request updated successfully."},  # First call (update_reason)
            {"code": 200, "message": "Status updated successfully."},   # Second call (change_all_status)
            {"code": 200, "message": "Log created successfully."}        # Third call (add_event)
        ]

        # Define the input data for the request
        request_data = {
            "request_id": 1,
            "reason": "Insufficient justification for the leave"
        }

        # Send a PUT request to the /reject_request route
        response = self.app.put('/reject_request', json=request_data)

        # Check the status code and the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["code"], 200)
        self.assertIn("Request rejection reason and status updated successfully.", response.json["message"])

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


class TestChangeStatusToApproved(flask_testing.TestCase):
    request_dates_app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"  # In-memory database
    request_dates_app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
    request_dates_app.config['TESTING'] = True

    def create_app(self):
        return request_dates_app

    def setUp(self):
        # Mock the database session
        self.patcher = patch('request_dates.db.session', new_callable=MagicMock)
        self.mock_db_session = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

class approveRequest(TestChangeStatusToApproved):
    @patch('view_requests.invoke_http')
    def test_approve_request(self, mock_invoke_http):
        # Set up the mock request date
        mock_request_date = RequestDates(
            request_date_id=1,
            request_id=1000,
            request_date=date(2024, 10, 17),
            request_shift='PM',
            request_status='Pending Approval'
        )

        # Configure the mock to return the test object
        mock_invoke_http.return_value = mock_request_date

        # Mock the employee query
        self.mock_db_session.query.return_value.filter_by.return_value.first.return_value = None  # No existing employee

        # Prepare to mock adding an employee
        test_employee = Employee(
            staff_id=999999,
            staff_fname='Jacob',
            staff_lname='Tan',
            dept='Engineering',
            position='Call Centre',
            country='Singapore',
            email='Jacob.Tan@allinone.com.sg',
            role=2,
            reporting_manager=None
        )

        # Mock adding the employee to the session
        self.mock_db_session.add.return_value = None  # Mocking the add method
        self.mock_db_session.commit.return_value = None  # Mocking the commit method

        # Simulate the creation of an employee
        self.mock_db_session.add(test_employee)
        self.mock_db_session.commit()

        # Prepare the input data
        request_data = {
            "request_id": 1000,
            "status": "Approved"
        }

        # Send a PUT request to the /change_all_status route
        response = self.client.put('/request_dates/change_all_status', json=request_data)

        # Check the status code and the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["code"], 200)
        self.assertIn("Request status for request ID 1000 updated to Approved.", response.json["message"])


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
