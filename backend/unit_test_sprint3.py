import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from view_schedule import app as view_schedule_app, db, Request, Employee, RequestDates  # Adjust import if needed

class TestGetOrgSchedule(unittest.TestCase):
    # Set up the Flask test client
    def setUp(self):
        view_schedule_app.testing = True  # Set testing mode directly on the app
        self.client = view_schedule_app.test_client()  # Use the test client directly
        self.maxDiff = None

    @patch('view_schedule.db')  # Adjust the patch path accordingly
    def test_get_org_schedule_success(self, mock_db):
        # Mock the query results for department count
        mock_query = MagicMock()
        mock_db.session.query.return_value = mock_query

        # Mocking the count query grouped by department
        mock_query.group_by.return_value.all.return_value = [
            ("HR", 2),  # Two employees in HR
            ("IT", 2)   # Two employees in IT
        ]

        # Mocking the employee schedule data with multiple joins and filters
        mock_query.join.return_value.join.return_value.all.return_value = [
            (1, "John", "Doe", "HR", "Manager", None, datetime(2024, 10, 16), "AM", "Approved"),
            (3, "Alice", "Johnson", "HR", "Staff", None, datetime(2024, 10, 16), "PM", "Approved"),
            (1, "John", "Doe", "HR", "Manager", None, datetime(2024, 10, 17), "PM", "Approved"),
            (2, "Jane", "Smith", "IT", "Developer", None, datetime(2024, 10, 16), "AM", "Pending Approval"),
            (4, "Bob", "Brown", "IT", "Manager", None, datetime(2024, 10, 17), "AM", "Approved"),
            (2, "Jane", "Smith", "IT", "Developer", None, datetime(2024, 10, 17), "PM", "Approved")
        ]

        # Make a GET request to the route
        response = self.client.get('/o_get_org_schedule')

        # Define the expected response format
        expected_response = {'HR': {'2024-09-03': {'AM': [], 'Full': [], 'PM': []}, '2024-09-04': {'AM': [], 'Full': [], 'PM': []}, '2024-09-05': {'AM': [], 'Full': [], 'PM': []}, '2024-09-06': {'AM': [], 'Full': [], 'PM': []}, '2024-09-07': {'AM': [], 'Full': [], 'PM': []}, '2024-09-08': {'AM': [], 'Full': [], 'PM': []}, '2024-09-09': {'AM': [], 'Full': [], 'PM': []}, '2024-09-10': {'AM': [], 'Full': [], 'PM': []}, '2024-09-11': {'AM': [], 'Full': [], 'PM': []}, '2024-09-12': {'AM': [], 'Full': [], 'PM': []}, '2024-09-13': {'AM': [], 'Full': [], 'PM': []}, '2024-09-14': {'AM': [], 'Full': [], 'PM': []}, '2024-09-15': {'AM': [], 'Full': [], 'PM': []}, '2024-09-16': {'AM': [], 'Full': [], 'PM': []}, '2024-09-17': {'AM': [], 'Full': [], 'PM': []}, '2024-09-18': {'AM': [], 'Full': [], 'PM': []}, '2024-09-19': {'AM': [], 'Full': [], 'PM': []}, '2024-09-20': {'AM': [], 'Full': [], 'PM': []}, '2024-09-21': {'AM': [], 'Full': [], 'PM': []}, '2024-09-22': {'AM': [], 'Full': [], 'PM': []}, '2024-09-23': {'AM': [], 'Full': [], 'PM': []}, '2024-09-24': {'AM': [], 'Full': [], 'PM': []}, '2024-09-25': {'AM': [], 'Full': [], 'PM': []}, '2024-09-26': {'AM': [], 'Full': [], 'PM': []}, '2024-09-27': {'AM': [], 'Full': [], 'PM': []}, '2024-09-28': {'AM': [], 'Full': [], 'PM': []}, '2024-09-29': {'AM': [], 'Full': [], 'PM': []}, '2024-09-30': {'AM': [], 'Full': [], 'PM': []}, '2024-10-01': {'AM': [], 'Full': [], 'PM': []}, '2024-10-02': {'AM': [], 'Full': [], 'PM': []}, '2024-10-03': {'AM': [], 'Full': [], 'PM': []}, '2024-10-04': {'AM': [], 'Full': [], 'PM': []}, '2024-10-05': {'AM': [], 'Full': [], 'PM': []}, '2024-10-06': {'AM': [], 'Full': [], 'PM': []}, '2024-10-07': {'AM': [], 'Full': [], 'PM': []}, '2024-10-08': {'AM': [], 'Full': [], 'PM': []}, '2024-10-09': {'AM': [], 'Full': [], 'PM': []}, '2024-10-10': {'AM': [], 'Full': [], 'PM': []}, '2024-10-11': {'AM': [], 'Full': [], 'PM': []}, '2024-10-12': {'AM': [], 'Full': [], 'PM': []}, '2024-10-13': {'AM': [], 'Full': [], 'PM': []}, '2024-10-14': {'AM': [], 'Full': [], 'PM': []}, '2024-10-15': {'AM': [], 'Full': [], 'PM': []}, '2024-10-16': {'AM': [], 'Full': [], 'PM': []}, '2024-10-17': {'AM': [], 'Full': [], 'PM': []}, '2024-10-18': {'AM': [], 'Full': [], 'PM': []}, '2024-10-19': {'AM': [], 'Full': [], 'PM': []}, '2024-10-20': {'AM': [], 'Full': [], 'PM': []}, '2024-10-21': {'AM': [], 'Full': [], 'PM': []}, '2024-10-22': {'AM': [], 'Full': [], 'PM': []}, '2024-10-23': {'AM': [], 'Full': [], 'PM': []}, '2024-10-24': {'AM': [], 'Full': [], 'PM': []}, '2024-10-25': {'AM': [], 'Full': [], 'PM': []}, '2024-10-26': {'AM': [], 'Full': [], 'PM': []}, '2024-10-27': {'AM': [], 'Full': [], 'PM': []}, '2024-10-28': {'AM': [], 'Full': [], 'PM': []}, '2024-10-29': {'AM': [], 'Full': [], 'PM': []}, '2024-10-30': {'AM': [], 'Full': [], 'PM': []}, '2024-10-31': {'AM': [], 'Full': [], 'PM': []}, '2024-11-01': {'AM': [], 'Full': [], 'PM': []}, '2024-11-02': {'AM': [], 'Full': [], 'PM': []}, '2024-11-03': {'AM': [], 'Full': [], 'PM': []}, '2024-11-04': {'AM': [], 'Full': [], 'PM': []}, '2024-11-05': {'AM': [], 'Full': [], 'PM': []}, '2024-11-06': {'AM': [], 'Full': [], 'PM': []}, '2024-11-07': {'AM': [], 'Full': [], 'PM': []}, '2024-11-08': {'AM': [], 'Full': [], 'PM': []}, '2024-11-09': {'AM': [], 'Full': [], 'PM': []}, '2024-11-10': {'AM': [], 'Full': [], 'PM': []}, '2024-11-11': {'AM': [], 'Full': [], 'PM': []}, '2024-11-12': {'AM': [], 'Full': [], 'PM': []}, '2024-11-13': {'AM': [], 'Full': [], 'PM': []}, '2024-11-14': {'AM': [], 'Full': [], 'PM': []}, '2024-11-15': {'AM': [], 'Full': [], 'PM': []}, '2024-11-16': {'AM': [], 'Full': [], 'PM': []}, '2024-11-17': {'AM': [], 'Full': [], 'PM': []}, '2024-11-18': {'AM': [], 'Full': [], 'PM': []}, '2024-11-19': {'AM': [], 'Full': [], 'PM': []}, '2024-11-20': {'AM': [], 'Full': [], 'PM': []}, '2024-11-21': {'AM': [], 'Full': [], 'PM': []}, '2024-11-22': {'AM': [], 'Full': [], 'PM': []}, '2024-11-23': {'AM': [], 'Full': [], 'PM': []}, '2024-11-24': {'AM': [], 'Full': [], 'PM': []}, '2024-11-25': {'AM': [], 'Full': [], 'PM': []}, '2024-11-26': {'AM': [], 'Full': [], 'PM': []}, '2024-11-27': {'AM': [], 'Full': [], 'PM': []}, '2024-11-28': {'AM': [], 'Full': [], 'PM': []}, '2024-11-29': {'AM': [], 'Full': [], 'PM': []}, '2024-11-30': {'AM': [], 'Full': [], 'PM': []}, '2024-12-01': {'AM': [], 'Full': [], 'PM': []}, '2024-12-02': {'AM': [], 'Full': [], 'PM': []}, '2024-12-03': {'AM': [], 'Full': [], 'PM': []}, '2024-12-04': {'AM': [], 'Full': [], 'PM': []}, '2024-12-05': {'AM': [], 'Full': [], 'PM': []}, '2024-12-06': {'AM': [], 'Full': [], 'PM': []}, '2024-12-07': {'AM': [], 'Full': [], 'PM': []}, '2024-12-08': {'AM': [], 'Full': [], 'PM': []}, '2024-12-09': {'AM': [], 'Full': [], 'PM': []}, '2024-12-10': {'AM': [], 'Full': [], 'PM': []}, '2024-12-11': {'AM': [], 'Full': [], 'PM': []}, '2024-12-12': {'AM': [], 'Full': [], 'PM': []}, '2024-12-13': {'AM': [], 'Full': [], 'PM': []}, '2024-12-14': {'AM': [], 'Full': [], 'PM': []}, '2024-12-15': {'AM': [], 'Full': [], 'PM': []}, '2024-12-16': {'AM': [], 'Full': [], 'PM': []}, '2024-12-17': {'AM': [], 'Full': [], 'PM': []}, '2024-12-18': {'AM': [], 'Full': [], 'PM': []}, '2024-12-19': {'AM': [], 'Full': [], 'PM': []}, '2024-12-20': {'AM': [], 'Full': [], 'PM': []}, '2024-12-21': {'AM': [], 'Full': [], 'PM': []}, '2024-12-22': {'AM': [], 'Full': [], 'PM': []}, '2024-12-23': {'AM': [], 'Full': [], 'PM': []}, '2024-12-24': {'AM': [], 'Full': [], 'PM': []}, '2024-12-25': {'AM': [], 'Full': [], 'PM': []}, '2024-12-26': {'AM': [], 'Full': [], 'PM': []}, '2024-12-27': {'AM': [], 'Full': [], 'PM': []}, '2024-12-28': {'AM': [], 'Full': [], 'PM': []}, '2024-12-29': {'AM': [], 'Full': [], 'PM': []}, '2024-12-30': {'AM': [], 'Full': [], 'PM': []}, '2024-12-31': {'AM': [], 'Full': [], 'PM': []}, '2025-01-01': {'AM': [], 'Full': [], 'PM': []}, '2025-01-02': {'AM': [], 'Full': [], 'PM': []}, '2025-01-03': {'AM': [], 'Full': [], 'PM': []}, '2025-01-04': {'AM': [], 'Full': [], 'PM': []}, '2025-01-05': {'AM': [], 'Full': [], 'PM': []}, '2025-01-06': {'AM': [], 'Full': [], 'PM': []}, '2025-01-07': {'AM': [], 'Full': [], 'PM': []}, '2025-01-08': {'AM': [], 'Full': [], 'PM': []}, '2025-01-09': {'AM': [], 'Full': [], 'PM': []}, '2025-01-10': {'AM': [], 'Full': [], 'PM': []}, '2025-01-11': {'AM': [], 'Full': [], 'PM': []}, '2025-01-12': {'AM': [], 'Full': [], 'PM': []}, '2025-01-13': {'AM': [], 'Full': [], 'PM': []}, '2025-01-14': {'AM': [], 'Full': [], 'PM': []}, '2025-01-15': {'AM': [], 'Full': [], 'PM': []}, '2025-01-16': {'AM': [], 'Full': [], 'PM': []}, '2025-01-17': {'AM': [], 'Full': [], 'PM': []}, '2025-01-18': {'AM': [], 'Full': [], 'PM': []}, '2025-01-19': {'AM': [], 'Full': [], 'PM': []}, '2025-01-20': {'AM': [], 'Full': [], 'PM': []}, '2025-01-21': {'AM': [], 'Full': [], 'PM': []}, '2025-01-22': {'AM': [], 'Full': [], 'PM': []}, '2025-01-23': {'AM': [], 'Full': [], 'PM': []}, '2025-01-24': {'AM': [], 'Full': [], 'PM': []}, '2025-01-25': {'AM': [], 'Full': [], 'PM': []}, '2025-01-26': {'AM': [], 'Full': [], 'PM': []}, '2025-01-27': {'AM': [], 'Full': [], 'PM': []}, '2025-01-28': {'AM': [], 'Full': [], 'PM': []}, '2025-01-29': {'AM': [], 'Full': [], 'PM': []}, '2025-01-30': {'AM': [], 'Full': [], 'PM': []}, '2025-01-31': {'AM': [], 'Full': [], 'PM': []}, 'num_employee': 2}, 'IT': {'2024-09-03': {'AM': [], 'Full': [], 'PM': []}, '2024-09-04': {'AM': [], 'Full': [], 'PM': []}, '2024-09-05': {'AM': [], 'Full': [], 'PM': []}, '2024-09-06': {'AM': [], 'Full': [], 'PM': []}, '2024-09-07': {'AM': [], 'Full': [], 'PM': []}, '2024-09-08': {'AM': [], 'Full': [], 'PM': []}, '2024-09-09': {'AM': [], 'Full': [], 'PM': []}, '2024-09-10': {'AM': [], 'Full': [], 'PM': []}, '2024-09-11': {'AM': [], 'Full': [], 'PM': []}, '2024-09-12': {'AM': [], 'Full': [], 'PM': []}, '2024-09-13': {'AM': [], 'Full': [], 'PM': []}, '2024-09-14': {'AM': [], 'Full': [], 'PM': []}, '2024-09-15': {'AM': [], 'Full': [], 'PM': []}, '2024-09-16': {'AM': [], 'Full': [], 'PM': []}, '2024-09-17': {'AM': [], 'Full': [], 'PM': []}, '2024-09-18': {'AM': [], 'Full': [], 'PM': []}, '2024-09-19': {'AM': [], 'Full': [], 'PM': []}, '2024-09-20': {'AM': [], 'Full': [], 'PM': []}, '2024-09-21': {'AM': [], 'Full': [], 'PM': []}, '2024-09-22': {'AM': [], 'Full': [], 'PM': []}, '2024-09-23': {'AM': [], 'Full': [], 'PM': []}, '2024-09-24': {'AM': [], 'Full': [], 'PM': []}, '2024-09-25': {'AM': [], 'Full': [], 'PM': []}, '2024-09-26': {'AM': [], 'Full': [], 'PM': []}, '2024-09-27': {'AM': [], 'Full': [], 'PM': []}, '2024-09-28': {'AM': [], 'Full': [], 'PM': []}, '2024-09-29': {'AM': [], 'Full': [], 'PM': []}, '2024-09-30': {'AM': [], 'Full': [], 'PM': []}, '2024-10-01': {'AM': [], 'Full': [], 'PM': []}, '2024-10-02': {'AM': [], 'Full': [], 'PM': []}, '2024-10-03': {'AM': [], 'Full': [], 'PM': []}, '2024-10-04': {'AM': [], 'Full': [], 'PM': []}, '2024-10-05': {'AM': [], 'Full': [], 'PM': []}, '2024-10-06': {'AM': [], 'Full': [], 'PM': []}, '2024-10-07': {'AM': [], 'Full': [], 'PM': []}, '2024-10-08': {'AM': [], 'Full': [], 'PM': []}, '2024-10-09': {'AM': [], 'Full': [], 'PM': []}, '2024-10-10': {'AM': [], 'Full': [], 'PM': []}, '2024-10-11': {'AM': [], 'Full': [], 'PM': []}, '2024-10-12': {'AM': [], 'Full': [], 'PM': []}, '2024-10-13': {'AM': [], 'Full': [], 'PM': []}, '2024-10-14': {'AM': [], 'Full': [], 'PM': []}, '2024-10-15': {'AM': [], 'Full': [], 'PM': []}, '2024-10-16': {'AM': [], 'Full': [], 'PM': []}, '2024-10-17': {'AM': [], 'Full': [], 'PM': []}, '2024-10-18': {'AM': [], 'Full': [], 'PM': []}, '2024-10-19': {'AM': [], 'Full': [], 'PM': []}, '2024-10-20': {'AM': [], 'Full': [], 'PM': []}, '2024-10-21': {'AM': [], 'Full': [], 'PM': []}, '2024-10-22': {'AM': [], 'Full': [], 'PM': []}, '2024-10-23': {'AM': [], 'Full': [], 'PM': []}, '2024-10-24': {'AM': [], 'Full': [], 'PM': []}, '2024-10-25': {'AM': [], 'Full': [], 'PM': []}, '2024-10-26': {'AM': [], 'Full': [], 'PM': []}, '2024-10-27': {'AM': [], 'Full': [], 'PM': []}, '2024-10-28': {'AM': [], 'Full': [], 'PM': []}, '2024-10-29': {'AM': [], 'Full': [], 'PM': []}, '2024-10-30': {'AM': [], 'Full': [], 'PM': []}, '2024-10-31': {'AM': [], 'Full': [], 'PM': []}, '2024-11-01': {'AM': [], 'Full': [], 'PM': []}, '2024-11-02': {'AM': [], 'Full': [], 'PM': []}, '2024-11-03': {'AM': [], 'Full': [], 'PM': []}, '2024-11-04': {'AM': [], 'Full': [], 'PM': []}, '2024-11-05': {'AM': [], 'Full': [], 'PM': []}, '2024-11-06': {'AM': [], 'Full': [], 'PM': []}, '2024-11-07': {'AM': [], 'Full': [], 'PM': []}, '2024-11-08': {'AM': [], 'Full': [], 'PM': []}, '2024-11-09': {'AM': [], 'Full': [], 'PM': []}, '2024-11-10': {'AM': [], 'Full': [], 'PM': []}, '2024-11-11': {'AM': [], 'Full': [], 'PM': []}, '2024-11-12': {'AM': [], 'Full': [], 'PM': []}, '2024-11-13': {'AM': [], 'Full': [], 'PM': []}, '2024-11-14': {'AM': [], 'Full': [], 'PM': []}, '2024-11-15': {'AM': [], 'Full': [], 'PM': []}, '2024-11-16': {'AM': [], 'Full': [], 'PM': []}, '2024-11-17': {'AM': [], 'Full': [], 'PM': []}, '2024-11-18': {'AM': [], 'Full': [], 'PM': []}, '2024-11-19': {'AM': [], 'Full': [], 'PM': []}, '2024-11-20': {'AM': [], 'Full': [], 'PM': []}, '2024-11-21': {'AM': [], 'Full': [], 'PM': []}, '2024-11-22': {'AM': [], 'Full': [], 'PM': []}, '2024-11-23': {'AM': [], 'Full': [], 'PM': []}, '2024-11-24': {'AM': [], 'Full': [], 'PM': []}, '2024-11-25': {'AM': [], 'Full': [], 'PM': []}, '2024-11-26': {'AM': [], 'Full': [], 'PM': []}, '2024-11-27': {'AM': [], 'Full': [], 'PM': []}, '2024-11-28': {'AM': [], 'Full': [], 'PM': []}, '2024-11-29': {'AM': [], 'Full': [], 'PM': []}, '2024-11-30': {'AM': [], 'Full': [], 'PM': []}, '2024-12-01': {'AM': [], 'Full': [], 'PM': []}, '2024-12-02': {'AM': [], 'Full': [], 'PM': []}, '2024-12-03': {'AM': [], 'Full': [], 'PM': []}, '2024-12-04': {'AM': [], 'Full': [], 'PM': []}, '2024-12-05': {'AM': [], 'Full': [], 'PM': []}, '2024-12-06': {'AM': [], 'Full': [], 'PM': []}, '2024-12-07': {'AM': [], 'Full': [], 'PM': []}, '2024-12-08': {'AM': [], 'Full': [], 'PM': []}, '2024-12-09': {'AM': [], 'Full': [], 'PM': []}, '2024-12-10': {'AM': [], 'Full': [], 'PM': []}, '2024-12-11': {'AM': [], 'Full': [], 'PM': []}, '2024-12-12': {'AM': [], 'Full': [], 'PM': []}, '2024-12-13': {'AM': [], 'Full': [], 'PM': []}, '2024-12-14': {'AM': [], 'Full': [], 'PM': []}, '2024-12-15': {'AM': [], 'Full': [], 'PM': []}, '2024-12-16': {'AM': [], 'Full': [], 'PM': []}, '2024-12-17': {'AM': [], 'Full': [], 'PM': []}, '2024-12-18': {'AM': [], 'Full': [], 'PM': []}, '2024-12-19': {'AM': [], 'Full': [], 'PM': []}, '2024-12-20': {'AM': [], 'Full': [], 'PM': []}, '2024-12-21': {'AM': [], 'Full': [], 'PM': []}, '2024-12-22': {'AM': [], 'Full': [], 'PM': []}, '2024-12-23': {'AM': [], 'Full': [], 'PM': []}, '2024-12-24': {'AM': [], 'Full': [], 'PM': []}, '2024-12-25': {'AM': [], 'Full': [], 'PM': []}, '2024-12-26': {'AM': [], 'Full': [], 'PM': []}, '2024-12-27': {'AM': [], 'Full': [], 'PM': []}, '2024-12-28': {'AM': [], 'Full': [], 'PM': []}, '2024-12-29': {'AM': [], 'Full': [], 'PM': []}, '2024-12-30': {'AM': [], 'Full': [], 'PM': []}, '2024-12-31': {'AM': [], 'Full': [], 'PM': []}, '2025-01-01': {'AM': [], 'Full': [], 'PM': []}, '2025-01-02': {'AM': [], 'Full': [], 'PM': []}, '2025-01-03': {'AM': [], 'Full': [], 'PM': []}, '2025-01-04': {'AM': [], 'Full': [], 'PM': []}, '2025-01-05': {'AM': [], 'Full': [], 'PM': []}, '2025-01-06': {'AM': [], 'Full': [], 'PM': []}, '2025-01-07': {'AM': [], 'Full': [], 'PM': []}, '2025-01-08': {'AM': [], 'Full': [], 'PM': []}, '2025-01-09': {'AM': [], 'Full': [], 'PM': []}, '2025-01-10': {'AM': [], 'Full': [], 'PM': []}, '2025-01-11': {'AM': [], 'Full': [], 'PM': []}, '2025-01-12': {'AM': [], 'Full': [], 'PM': []}, '2025-01-13': {'AM': [], 'Full': [], 'PM': []}, '2025-01-14': {'AM': [], 'Full': [], 'PM': []}, '2025-01-15': {'AM': [], 'Full': [], 'PM': []}, '2025-01-16': {'AM': [], 'Full': [], 'PM': []}, '2025-01-17': {'AM': [], 'Full': [], 'PM': []}, '2025-01-18': {'AM': [], 'Full': [], 'PM': []}, '2025-01-19': {'AM': [], 'Full': [], 'PM': []}, '2025-01-20': {'AM': [], 'Full': [], 'PM': []}, '2025-01-21': {'AM': [], 'Full': [], 'PM': []}, '2025-01-22': {'AM': [], 'Full': [], 'PM': []}, '2025-01-23': {'AM': [], 'Full': [], 'PM': []}, '2025-01-24': {'AM': [], 'Full': [], 'PM': []}, '2025-01-25': {'AM': [], 'Full': [], 'PM': []}, '2025-01-26': {'AM': [], 'Full': [], 'PM': []}, '2025-01-27': {'AM': [], 'Full': [], 'PM': []}, '2025-01-28': {'AM': [], 'Full': [], 'PM': []}, '2025-01-29': {'AM': [], 'Full': [], 'PM': []}, '2025-01-30': {'AM': [], 'Full': [], 'PM': []}, '2025-01-31': {'AM': [], 'Full': [], 'PM': []}, 'num_employee': 2}}

        # Assert the response status and content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected_response)

    @patch('view_schedule.db')  # Adjust the patch path accordingly
    def test_get_org_schedule_error(self, mock_db):
        # Mock the database query to raise an exception
        mock_db.session.query.side_effect = Exception("Database connection error")

        # Make a GET request to the route
        response = self.client.get('/o_get_org_schedule')

        # Assert that the response is a 500 error
        self.assertEqual(response.status_code, 500)

        # Assert the error message is as expected
        expected_error_response = {
            "message": "An error occurred while retrieving the schedule.",
            "error": "Database connection error"
        }
        self.assertEqual(response.json, expected_error_response)





class TestGetManagerSchedule(unittest.TestCase):
    # Set up the Flask test client
    def setUp(self):
        view_schedule_app.testing = True  # Set testing mode
        self.client = view_schedule_app.test_client()  # Use the test client
        self.maxDiff = None

    @patch('view_schedule.invoke_http')  # Mock the invoke_http function
    @patch('view_schedule.db')  # Mock the database session
    def test_get_team_schedule_success(self, mock_db, mock_invoke_http):
        # Mock the database query results
        mock_query = MagicMock()
        mock_db.session.query.return_value = mock_query

        # Mock responses for employee details and all employees
        mock_invoke_http.side_effect = [
            # Response for employee details
            {
                "code": 200,
                "data": {
                    "staff_id": 1,
                    "staff_fname": "John",
                    "staff_lname": "Doe",
                    "dept": "IT",
                    "position": "Manager",
                    "reporting_manager": None,
                    "role": 3
                }
            },
            # Response for all employees
            {
                "code": 200,
                "data": [
                    {
                        "staff_id": 2,
                        "reporting_manager": 1,
                        "staff_name": "Jane Smith",
                        "dept": "IT",
                        "position": "Developer"
                    },
                    {
                        "staff_id": 3,
                        "reporting_manager": 1,
                        "staff_name": "Alice Johnson",
                        "dept": "IT",
                        "position": "IT Specialist"
                    }
                ]
            }
        ]

        # Mock the response from the database for request data
        mock_query.join.return_value.join.return_value.all.return_value = [
            (1, "John", "Doe", "HR", "Manager", None, datetime(2024, 10, 17), "Full", "Approved"),
            (3, "Alice", "Johnson", "HR", "HR Specialist", 1, datetime(2024, 10, 16), "Full", "Approved")
        ]

        # Make a GET request to the route
        response = self.client.get('/m_get_team_schedule/1')

        # Define the expected response
        expected_response = {'IT': {'2024-09-03': {'AM': [], 'Full': [], 'PM': []}, '2024-09-04': {'AM': [], 'Full': [], 'PM': []}, '2024-09-05': {'AM': [], 'Full': [], 'PM': []}, '2024-09-06': {'AM': [], 'Full': [], 'PM': []}, '2024-09-07': {'AM': [], 'Full': [], 'PM': []}, '2024-09-08': {'AM': [], 'Full': [], 'PM': []}, '2024-09-09': {'AM': [], 'Full': [], 'PM': []}, '2024-09-10': {'AM': [], 'Full': [], 'PM': []}, '2024-09-11': {'AM': [], 'Full': [], 'PM': []}, '2024-09-12': {'AM': [], 'Full': [], 'PM': []}, '2024-09-13': {'AM': [], 'Full': [], 'PM': []}, '2024-09-14': {'AM': [], 'Full': [], 'PM': []}, '2024-09-15': {'AM': [], 'Full': [], 'PM': []}, '2024-09-16': {'AM': [], 'Full': [], 'PM': []}, '2024-09-17': {'AM': [], 'Full': [], 'PM': []}, '2024-09-18': {'AM': [], 'Full': [], 'PM': []}, '2024-09-19': {'AM': [], 'Full': [], 'PM': []}, '2024-09-20': {'AM': [], 'Full': [], 'PM': []}, '2024-09-21': {'AM': [], 'Full': [], 'PM': []}, '2024-09-22': {'AM': [], 'Full': [], 'PM': []}, '2024-09-23': {'AM': [], 'Full': [], 'PM': []}, '2024-09-24': {'AM': [], 'Full': [], 'PM': []}, '2024-09-25': {'AM': [], 'Full': [], 'PM': []}, '2024-09-26': {'AM': [], 'Full': [], 'PM': []}, '2024-09-27': {'AM': [], 'Full': [], 'PM': []}, '2024-09-28': {'AM': [], 'Full': [], 'PM': []}, '2024-09-29': {'AM': [], 'Full': [], 'PM': []}, '2024-09-30': {'AM': [], 'Full': [], 'PM': []}, '2024-10-01': {'AM': [], 'Full': [], 'PM': []}, '2024-10-02': {'AM': [], 'Full': [], 'PM': []}, '2024-10-03': {'AM': [], 'Full': [], 'PM': []}, '2024-10-04': {'AM': [], 'Full': [], 'PM': []}, '2024-10-05': {'AM': [], 'Full': [], 'PM': []}, '2024-10-06': {'AM': [], 'Full': [], 'PM': []}, '2024-10-07': {'AM': [], 'Full': [], 'PM': []}, '2024-10-08': {'AM': [], 'Full': [], 'PM': []}, '2024-10-09': {'AM': [], 'Full': [], 'PM': []}, '2024-10-10': {'AM': [], 'Full': [], 'PM': []}, '2024-10-11': {'AM': [], 'Full': [], 'PM': []}, '2024-10-12': {'AM': [], 'Full': [], 'PM': []}, '2024-10-13': {'AM': [], 'Full': [], 'PM': []}, '2024-10-14': {'AM': [], 'Full': [], 'PM': []}, '2024-10-15': {'AM': [], 'Full': [], 'PM': []}, '2024-10-16': {'AM': [], 'Full': [], 'PM': []}, '2024-10-17': {'AM': [], 'Full': [], 'PM': []}, '2024-10-18': {'AM': [], 'Full': [], 'PM': []}, '2024-10-19': {'AM': [], 'Full': [], 'PM': []}, '2024-10-20': {'AM': [], 'Full': [], 'PM': []}, '2024-10-21': {'AM': [], 'Full': [], 'PM': []}, '2024-10-22': {'AM': [], 'Full': [], 'PM': []}, '2024-10-23': {'AM': [], 'Full': [], 'PM': []}, '2024-10-24': {'AM': [], 'Full': [], 'PM': []}, '2024-10-25': {'AM': [], 'Full': [], 'PM': []}, '2024-10-26': {'AM': [], 'Full': [], 'PM': []}, '2024-10-27': {'AM': [], 'Full': [], 'PM': []}, '2024-10-28': {'AM': [], 'Full': [], 'PM': []}, '2024-10-29': {'AM': [], 'Full': [], 'PM': []}, '2024-10-30': {'AM': [], 'Full': [], 'PM': []}, '2024-10-31': {'AM': [], 'Full': [], 'PM': []}, '2024-11-01': {'AM': [], 'Full': [], 'PM': []}, '2024-11-02': {'AM': [], 'Full': [], 'PM': []}, '2024-11-03': {'AM': [], 'Full': [], 'PM': []}, '2024-11-04': {'AM': [], 'Full': [], 'PM': []}, '2024-11-05': {'AM': [], 'Full': [], 'PM': []}, '2024-11-06': {'AM': [], 'Full': [], 'PM': []}, '2024-11-07': {'AM': [], 'Full': [], 'PM': []}, '2024-11-08': {'AM': [], 'Full': [], 'PM': []}, '2024-11-09': {'AM': [], 'Full': [], 'PM': []}, '2024-11-10': {'AM': [], 'Full': [], 'PM': []}, '2024-11-11': {'AM': [], 'Full': [], 'PM': []}, '2024-11-12': {'AM': [], 'Full': [], 'PM': []}, '2024-11-13': {'AM': [], 'Full': [], 'PM': []}, '2024-11-14': {'AM': [], 'Full': [], 'PM': []}, '2024-11-15': {'AM': [], 'Full': [], 'PM': []}, '2024-11-16': {'AM': [], 'Full': [], 'PM': []}, '2024-11-17': {'AM': [], 'Full': [], 'PM': []}, '2024-11-18': {'AM': [], 'Full': [], 'PM': []}, '2024-11-19': {'AM': [], 'Full': [], 'PM': []}, '2024-11-20': {'AM': [], 'Full': [], 'PM': []}, '2024-11-21': {'AM': [], 'Full': [], 'PM': []}, '2024-11-22': {'AM': [], 'Full': [], 'PM': []}, '2024-11-23': {'AM': [], 'Full': [], 'PM': []}, '2024-11-24': {'AM': [], 'Full': [], 'PM': []}, '2024-11-25': {'AM': [], 'Full': [], 'PM': []}, '2024-11-26': {'AM': [], 'Full': [], 'PM': []}, '2024-11-27': {'AM': [], 'Full': [], 'PM': []}, '2024-11-28': {'AM': [], 'Full': [], 'PM': []}, '2024-11-29': {'AM': [], 'Full': [], 'PM': []}, '2024-11-30': {'AM': [], 'Full': [], 'PM': []}, '2024-12-01': {'AM': [], 'Full': [], 'PM': []}, '2024-12-02': {'AM': [], 'Full': [], 'PM': []}, '2024-12-03': {'AM': [], 'Full': [], 'PM': []}, '2024-12-04': {'AM': [], 'Full': [], 'PM': []}, '2024-12-05': {'AM': [], 'Full': [], 'PM': []}, '2024-12-06': {'AM': [], 'Full': [], 'PM': []}, '2024-12-07': {'AM': [], 'Full': [], 'PM': []}, '2024-12-08': {'AM': [], 'Full': [], 'PM': []}, '2024-12-09': {'AM': [], 'Full': [], 'PM': []}, '2024-12-10': {'AM': [], 'Full': [], 'PM': []}, '2024-12-11': {'AM': [], 'Full': [], 'PM': []}, '2024-12-12': {'AM': [], 'Full': [], 'PM': []}, '2024-12-13': {'AM': [], 'Full': [], 'PM': []}, '2024-12-14': {'AM': [], 'Full': [], 'PM': []}, '2024-12-15': {'AM': [], 'Full': [], 'PM': []}, '2024-12-16': {'AM': [], 'Full': [], 'PM': []}, '2024-12-17': {'AM': [], 'Full': [], 'PM': []}, '2024-12-18': {'AM': [], 'Full': [], 'PM': []}, '2024-12-19': {'AM': [], 'Full': [], 'PM': []}, '2024-12-20': {'AM': [], 'Full': [], 'PM': []}, '2024-12-21': {'AM': [], 'Full': [], 'PM': []}, '2024-12-22': {'AM': [], 'Full': [], 'PM': []}, '2024-12-23': {'AM': [], 'Full': [], 'PM': []}, '2024-12-24': {'AM': [], 'Full': [], 'PM': []}, '2024-12-25': {'AM': [], 'Full': [], 'PM': []}, '2024-12-26': {'AM': [], 'Full': [], 'PM': []}, '2024-12-27': {'AM': [], 'Full': [], 'PM': []}, '2024-12-28': {'AM': [], 'Full': [], 'PM': []}, '2024-12-29': {'AM': [], 'Full': [], 'PM': []}, '2024-12-30': {'AM': [], 'Full': [], 'PM': []}, '2024-12-31': {'AM': [], 'Full': [], 'PM': []}, '2025-01-01': {'AM': [], 'Full': [], 'PM': []}, '2025-01-02': {'AM': [], 'Full': [], 'PM': []}, '2025-01-03': {'AM': [], 'Full': [], 'PM': []}, '2025-01-04': {'AM': [], 'Full': [], 'PM': []}, '2025-01-05': {'AM': [], 'Full': [], 'PM': []}, '2025-01-06': {'AM': [], 'Full': [], 'PM': []}, '2025-01-07': {'AM': [], 'Full': [], 'PM': []}, '2025-01-08': {'AM': [], 'Full': [], 'PM': []}, '2025-01-09': {'AM': [], 'Full': [], 'PM': []}, '2025-01-10': {'AM': [], 'Full': [], 'PM': []}, '2025-01-11': {'AM': [], 'Full': [], 'PM': []}, '2025-01-12': {'AM': [], 'Full': [], 'PM': []}, '2025-01-13': {'AM': [], 'Full': [], 'PM': []}, '2025-01-14': {'AM': [], 'Full': [], 'PM': []}, '2025-01-15': {'AM': [], 'Full': [], 'PM': []}, '2025-01-16': {'AM': [], 'Full': [], 'PM': []}, '2025-01-17': {'AM': [], 'Full': [], 'PM': []}, '2025-01-18': {'AM': [], 'Full': [], 'PM': []}, '2025-01-19': {'AM': [], 'Full': [], 'PM': []}, '2025-01-20': {'AM': [], 'Full': [], 'PM': []}, '2025-01-21': {'AM': [], 'Full': [], 'PM': []}, '2025-01-22': {'AM': [], 'Full': [], 'PM': []}, '2025-01-23': {'AM': [], 'Full': [], 'PM': []}, '2025-01-24': {'AM': [], 'Full': [], 'PM': []}, '2025-01-25': {'AM': [], 'Full': [], 'PM': []}, '2025-01-26': {'AM': [], 'Full': [], 'PM': []}, '2025-01-27': {'AM': [], 'Full': [], 'PM': []}, '2025-01-28': {'AM': [], 'Full': [], 'PM': []}, '2025-01-29': {'AM': [], 'Full': [], 'PM': []}, '2025-01-30': {'AM': [], 'Full': [], 'PM': []}, '2025-01-31': {'AM': [], 'Full': [], 'PM': []}, 'num_employee': 2}}

        # Assert the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected_response)

    @patch('view_schedule.invoke_http')  # Mock the invoke_http function
    def test_get_team_schedule_error(self, mock_invoke_http):
        # Mock the response to simulate an error
        mock_invoke_http.side_effect = Exception("Some error occurred")

        # Make a GET request to the route
        response = self.client.get('/m_get_team_schedule/1')

        # Assert the response
        self.assertEqual(response.status_code, 500)
        self.assertIn("An error occurred while retrieving the schedule.", response.json["message"])



class TestGetTeamSchedule(unittest.TestCase):
    def setUp(self):
        view_schedule_app.testing = True
        self.client = view_schedule_app.test_client()
        self.maxDiff = None

    @patch('view_schedule.invoke_http')  # Mock the invoke_http function
    @patch('view_schedule.db')  # Mock the database session
    def test_get_team_schedule_success(self, mock_db, mock_invoke_http):
        # Mock response from the employee details endpoint
        mock_invoke_http.return_value = {
            "data": {"dept": "HR", "position": "Account Manager", "role": "Employee", "reporting_manager": 1}
        }

        # Mock the response from the database for employee count in dept, position, role
        mock_db.session.query.return_value.filter.return_value.group_by.return_value.first.return_value = (
            "HR", 2
        )

        # Mock the response from the database for request data
        mock_db.session.query.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = [
            (1, "John", "Doe", "HR", "Account Manager", None, datetime(2024, 10, 17), "Full", "Approved"),
            (3, "Alice", "Johnson", "HR", "Account Manager", 1, datetime(2024, 10, 16), "Full", "Approved")
        ]

        # Define the expected response based on dept_dict structure
        expected_response = {'HR': {'2024-09-03': {'AM': [], 'Full': [], 'PM': []}, '2024-09-04': {'AM': [], 'Full': [], 'PM': []}, '2024-09-05': {'AM': [], 'Full': [], 'PM': []}, '2024-09-06': {'AM': [], 'Full': [], 'PM': []}, '2024-09-07': {'AM': [], 'Full': [], 'PM': []}, '2024-09-08': {'AM': [], 'Full': [], 'PM': []}, '2024-09-09': {'AM': [], 'Full': [], 'PM': []}, '2024-09-10': {'AM': [], 'Full': [], 'PM': []}, '2024-09-11': {'AM': [], 'Full': [], 'PM': []}, '2024-09-12': {'AM': [], 'Full': [], 'PM': []}, '2024-09-13': {'AM': [], 'Full': [], 'PM': []}, '2024-09-14': {'AM': [], 'Full': [], 'PM': []}, '2024-09-15': {'AM': [], 'Full': [], 'PM': []}, '2024-09-16': {'AM': [], 'Full': [], 'PM': []}, '2024-09-17': {'AM': [], 'Full': [], 'PM': []}, '2024-09-18': {'AM': [], 'Full': [], 'PM': []}, '2024-09-19': {'AM': [], 'Full': [], 'PM': []}, '2024-09-20': {'AM': [], 'Full': [], 'PM': []}, '2024-09-21': {'AM': [], 'Full': [], 'PM': []}, '2024-09-22': {'AM': [], 'Full': [], 'PM': []}, '2024-09-23': {'AM': [], 'Full': [], 'PM': []}, '2024-09-24': {'AM': [], 'Full': [], 'PM': []}, '2024-09-25': {'AM': [], 'Full': [], 'PM': []}, '2024-09-26': {'AM': [], 'Full': [], 'PM': []}, '2024-09-27': {'AM': [], 'Full': [], 'PM': []}, '2024-09-28': {'AM': [], 'Full': [], 'PM': []}, '2024-09-29': {'AM': [], 'Full': [], 'PM': []}, '2024-09-30': {'AM': [], 'Full': [], 'PM': []}, '2024-10-01': {'AM': [], 'Full': [], 'PM': []}, '2024-10-02': {'AM': [], 'Full': [], 'PM': []}, '2024-10-03': {'AM': [], 'Full': [], 'PM': []}, '2024-10-04': {'AM': [], 'Full': [], 'PM': []}, '2024-10-05': {'AM': [], 'Full': [], 'PM': []}, '2024-10-06': {'AM': [], 'Full': [], 'PM': []}, '2024-10-07': {'AM': [], 'Full': [], 'PM': []}, '2024-10-08': {'AM': [], 'Full': [], 'PM': []}, '2024-10-09': {'AM': [], 'Full': [], 'PM': []}, '2024-10-10': {'AM': [], 'Full': [], 'PM': []}, '2024-10-11': {'AM': [], 'Full': [], 'PM': []}, '2024-10-12': {'AM': [], 'Full': [], 'PM': []}, '2024-10-13': {'AM': [], 'Full': [], 'PM': []}, '2024-10-14': {'AM': [], 'Full': [], 'PM': []}, '2024-10-15': {'AM': [], 'Full': [], 'PM': []}, '2024-10-16': {'AM': [], 'Full': [{'name': 'Alice Johnson', 'reporting_manager': 1, 'request_status': 'Approved', 'role': 'Account Manager', 'staff_id': 3}], 'PM': []}, '2024-10-17': {'AM': [], 'Full': [{'name': 'John Doe', 'reporting_manager': None, 'request_status': 'Approved', 'role': 'Account Manager', 'staff_id': 1}], 'PM': []}, '2024-10-18': {'AM': [], 'Full': [], 'PM': []}, '2024-10-19': {'AM': [], 'Full': [], 'PM': []}, '2024-10-20': {'AM': [], 'Full': [], 'PM': []}, '2024-10-21': {'AM': [], 'Full': [], 'PM': []}, '2024-10-22': {'AM': [], 'Full': [], 'PM': []}, '2024-10-23': {'AM': [], 'Full': [], 'PM': []}, '2024-10-24': {'AM': [], 'Full': [], 'PM': []}, '2024-10-25': {'AM': [], 'Full': [], 'PM': []}, '2024-10-26': {'AM': [], 'Full': [], 'PM': []}, '2024-10-27': {'AM': [], 'Full': [], 'PM': []}, '2024-10-28': {'AM': [], 'Full': [], 'PM': []}, '2024-10-29': {'AM': [], 'Full': [], 'PM': []}, '2024-10-30': {'AM': [], 'Full': [], 'PM': []}, '2024-10-31': {'AM': [], 'Full': [], 'PM': []}, '2024-11-01': {'AM': [], 'Full': [], 'PM': []}, '2024-11-02': {'AM': [], 'Full': [], 'PM': []}, '2024-11-03': {'AM': [], 'Full': [], 'PM': []}, '2024-11-04': {'AM': [], 'Full': [], 'PM': []}, '2024-11-05': {'AM': [], 'Full': [], 'PM': []}, '2024-11-06': {'AM': [], 'Full': [], 'PM': []}, '2024-11-07': {'AM': [], 'Full': [], 'PM': []}, '2024-11-08': {'AM': [], 'Full': [], 'PM': []}, '2024-11-09': {'AM': [], 'Full': [], 'PM': []}, '2024-11-10': {'AM': [], 'Full': [], 'PM': []}, '2024-11-11': {'AM': [], 'Full': [], 'PM': []}, '2024-11-12': {'AM': [], 'Full': [], 'PM': []}, '2024-11-13': {'AM': [], 'Full': [], 'PM': []}, '2024-11-14': {'AM': [], 'Full': [], 'PM': []}, '2024-11-15': {'AM': [], 'Full': [], 'PM': []}, '2024-11-16': {'AM': [], 'Full': [], 'PM': []}, '2024-11-17': {'AM': [], 'Full': [], 'PM': []}, '2024-11-18': {'AM': [], 'Full': [], 'PM': []}, '2024-11-19': {'AM': [], 'Full': [], 'PM': []}, '2024-11-20': {'AM': [], 'Full': [], 'PM': []}, '2024-11-21': {'AM': [], 'Full': [], 'PM': []}, '2024-11-22': {'AM': [], 'Full': [], 'PM': []}, '2024-11-23': {'AM': [], 'Full': [], 'PM': []}, '2024-11-24': {'AM': [], 'Full': [], 'PM': []}, '2024-11-25': {'AM': [], 'Full': [], 'PM': []}, '2024-11-26': {'AM': [], 'Full': [], 'PM': []}, '2024-11-27': {'AM': [], 'Full': [], 'PM': []}, '2024-11-28': {'AM': [], 'Full': [], 'PM': []}, '2024-11-29': {'AM': [], 'Full': [], 'PM': []}, '2024-11-30': {'AM': [], 'Full': [], 'PM': []}, '2024-12-01': {'AM': [], 'Full': [], 'PM': []}, '2024-12-02': {'AM': [], 'Full': [], 'PM': []}, '2024-12-03': {'AM': [], 'Full': [], 'PM': []}, '2024-12-04': {'AM': [], 'Full': [], 'PM': []}, '2024-12-05': {'AM': [], 'Full': [], 'PM': []}, '2024-12-06': {'AM': [], 'Full': [], 'PM': []}, '2024-12-07': {'AM': [], 'Full': [], 'PM': []}, '2024-12-08': {'AM': [], 'Full': [], 'PM': []}, '2024-12-09': {'AM': [], 'Full': [], 'PM': []}, '2024-12-10': {'AM': [], 'Full': [], 'PM': []}, '2024-12-11': {'AM': [], 'Full': [], 'PM': []}, '2024-12-12': {'AM': [], 'Full': [], 'PM': []}, '2024-12-13': {'AM': [], 'Full': [], 'PM': []}, '2024-12-14': {'AM': [], 'Full': [], 'PM': []}, '2024-12-15': {'AM': [], 'Full': [], 'PM': []}, '2024-12-16': {'AM': [], 'Full': [], 'PM': []}, '2024-12-17': {'AM': [], 'Full': [], 'PM': []}, '2024-12-18': {'AM': [], 'Full': [], 'PM': []}, '2024-12-19': {'AM': [], 'Full': [], 'PM': []}, '2024-12-20': {'AM': [], 'Full': [], 'PM': []}, '2024-12-21': {'AM': [], 'Full': [], 'PM': []}, '2024-12-22': {'AM': [], 'Full': [], 'PM': []}, '2024-12-23': {'AM': [], 'Full': [], 'PM': []}, '2024-12-24': {'AM': [], 'Full': [], 'PM': []}, '2024-12-25': {'AM': [], 'Full': [], 'PM': []}, '2024-12-26': {'AM': [], 'Full': [], 'PM': []}, '2024-12-27': {'AM': [], 'Full': [], 'PM': []}, '2024-12-28': {'AM': [], 'Full': [], 'PM': []}, '2024-12-29': {'AM': [], 'Full': [], 'PM': []}, '2024-12-30': {'AM': [], 'Full': [], 'PM': []}, '2024-12-31': {'AM': [], 'Full': [], 'PM': []}, '2025-01-01': {'AM': [], 'Full': [], 'PM': []}, '2025-01-02': {'AM': [], 'Full': [], 'PM': []}, '2025-01-03': {'AM': [], 'Full': [], 'PM': []}, '2025-01-04': {'AM': [], 'Full': [], 'PM': []}, '2025-01-05': {'AM': [], 'Full': [], 'PM': []}, '2025-01-06': {'AM': [], 'Full': [], 'PM': []}, '2025-01-07': {'AM': [], 'Full': [], 'PM': []}, '2025-01-08': {'AM': [], 'Full': [], 'PM': []}, '2025-01-09': {'AM': [], 'Full': [], 'PM': []}, '2025-01-10': {'AM': [], 'Full': [], 'PM': []}, '2025-01-11': {'AM': [], 'Full': [], 'PM': []}, '2025-01-12': {'AM': [], 'Full': [], 'PM': []}, '2025-01-13': {'AM': [], 'Full': [], 'PM': []}, '2025-01-14': {'AM': [], 'Full': [], 'PM': []}, '2025-01-15': {'AM': [], 'Full': [], 'PM': []}, '2025-01-16': {'AM': [], 'Full': [], 'PM': []}, '2025-01-17': {'AM': [], 'Full': [], 'PM': []}, '2025-01-18': {'AM': [], 'Full': [], 'PM': []}, '2025-01-19': {'AM': [], 'Full': [], 'PM': []}, '2025-01-20': {'AM': [], 'Full': [], 'PM': []}, '2025-01-21': {'AM': [], 'Full': [], 'PM': []}, '2025-01-22': {'AM': [], 'Full': [], 'PM': []}, '2025-01-23': {'AM': [], 'Full': [], 'PM': []}, '2025-01-24': {'AM': [], 'Full': [], 'PM': []}, '2025-01-25': {'AM': [], 'Full': [], 'PM': []}, '2025-01-26': {'AM': [], 'Full': [], 'PM': []}, '2025-01-27': {'AM': [], 'Full': [], 'PM': []}, '2025-01-28': {'AM': [], 'Full': [], 'PM': []}, '2025-01-29': {'AM': [], 'Full': [], 'PM': []}, '2025-01-30': {'AM': [], 'Full': [], 'PM': []}, '2025-01-31': {'AM': [], 'Full': [], 'PM': []}, 'num_employee': 2}}

        # Make a GET request to the route
        response = self.client.get('/s_get_team_schedule/1')

        # Assert the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected_response)

    @patch('view_schedule.invoke_http')  # Mock the invoke_http function
    def test_get_team_schedule_error(self, mock_invoke_http):
        # Mock the response to simulate an error
        mock_invoke_http.side_effect = Exception("Some error occurred")

        # Make a GET request to the route
        response = self.client.get('/s_get_team_schedule/1')

        # Assert the response
        self.assertEqual(response.status_code, 500)
        self.assertIn("An error occurred while retrieving the schedule.", response.json["message"])


if __name__ == '__main__':
    unittest.main()
