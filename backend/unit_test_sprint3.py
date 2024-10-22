import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from view_schedule import app as view_schedule_app, db, Request, Employee, RequestDates  # Adjust import if needed

class TestGetOrgSchedule(unittest.TestCase):
    # Set up the Flask test client
    def setUp(self):
        view_schedule_app.testing = True  # Set testing mode directly on the app
        self.client = view_schedule_app.test_client()  # Use the test client directly
        self.maxDiff = None

    @patch('view_schedule.db')  # Adjust the patch path accordingly
    def test_get_org_schedule_success(self, mock_db):
        # Mock the query results
        mock_query = MagicMock()
        mock_db.session.query.return_value = mock_query
        mock_query.join.return_value.join.return_value.filter.return_value.all.return_value = [
            (1, "John", "Doe", "HR", "Manager", datetime(2024, 10, 16), "Morning", "Approved"),
            (3, "Alice", "Johnson", "HR", "Staff", datetime(2024, 10, 16), "Evening", "Approved"),
            (1, "John", "Doe", "HR", "Manager", datetime(2024, 10, 17), "Evening", "Pending Approval"),
            (2, "Jane", "Smith", "IT", "Developer", datetime(2024, 10, 16), "Afternoon", "Pending Approval"),
            (4, "Bob", "Brown", "IT", "Manager", datetime(2024, 10, 17), "Morning", "Approved"),
            (2, "Jane", "Smith", "IT", "Developer", datetime(2024, 10, 17), "Afternoon", "Approved")
        ]

        # Make a GET request to the route
        response = self.client.get('/o_get_org_schedule')

        # Define the expected response
        expected_response = {
            "HR": {
                "2024-10-16": [
                    {"staff_name": "John Doe", "staff_id": 1, "position": "Manager", "schedule": ["WFH - Morning"]},
                    {"staff_name": "Alice Johnson", "staff_id": 3, "position": "Staff", "schedule": ["WFH - Evening"]}
                ],
                "2024-10-17": [
                    {"staff_name": "John Doe", "staff_id": 1, "position": "Manager", "schedule": ["Pending - Evening"]}
                ]
            },
            "IT": {
                "2024-10-16": [
                    {"staff_name": "Jane Smith", "staff_id": 2, "position": "Developer", "schedule": ["Pending - Afternoon"]}
                ],
                "2024-10-17": [
                    {"staff_name": "Bob Brown", "staff_id": 4, "position": "Manager", "schedule": ["WFH - Morning"]},
                    {"staff_name": "Jane Smith", "staff_id": 2, "position": "Developer", "schedule": ["WFH - Afternoon"]}
                ]
            }
        }

        # Assert the response
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


import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from view_schedule import app as view_schedule_app, db, Request, Employee, RequestDates  # Adjust import if needed

class TestGetManagerSchedule(unittest.TestCase):
    # Set up the Flask test client
    def setUp(self):
        view_schedule_app.testing = True  # Set testing mode directly on the app
        self.client = view_schedule_app.test_client()  # Use the test client directly
        self.maxDiff = None

    @patch('view_schedule.invoke_http')  # Mock the invoke_http function
    @patch('view_schedule.db')  # Adjust the patch path accordingly
    def test_get_manager_schedule_success(self, mock_db, mock_invoke_http):
        # Mock the invoke_http response to return employee data
        mock_invoke_http.return_value = {
            "data": [
                {"staff_id": 1, "staff_name": "John Doe", "dept": "HR", "position": "Manager", "reporting_manager": None},
                {"staff_id": 2, "staff_name": "Jane Smith", "dept": "IT", "position": "Developer", "reporting_manager": 1},
                {"staff_id": 3, "staff_name": "Alice Johnson", "dept": "HR", "position": "HR Specialist", "reporting_manager": 1},
                {"staff_id": 4, "staff_name": "Bob Brown", "dept": "IT", "position": "Developer", "reporting_manager": 2},
            ]
        }

        # Mock the query results
        mock_query = MagicMock()
        mock_db.session.query.return_value = mock_query
        mock_query.join.return_value.join.return_value.filter.return_value.all.return_value = [
            (2, "Jane", "Smith", "IT", "Developer", datetime(2024, 10, 16), "Afternoon", "Pending Approval"),
            (4, "Bob", "Brown", "IT", "Developer", datetime(2024, 10, 17), "Morning", "Approved"),
            (3, "Alice", "Johnson", "HR", "HR Specialist", datetime(2024, 10, 16), "Evening", "Approved"),
            (1, "John", "Doe", "HR", "Manager", datetime(2024, 10, 17), "Evening", "Pending Approval"),
        ]

        # Make a GET request to the route
        response = self.client.get('/m_get_team_schedule/1')

        # Define the expected response
        expected_response = {
            'HR': {
                '2024-10-16': [
                    {
                        'staff_name': 'Alice Johnson',
                        'staff_id': 3,
                        'position': 'HR Specialist',
                        'schedule': ['WFH - Evening']
                    }
                ]
            },
            'IT': {
                '2024-10-16': [
                    {
                        'staff_name': 'Jane Smith',
                        'staff_id': 2,
                        'position': 'Developer',
                        'schedule': ['Pending - Afternoon']
                    }
                ],
                '2024-10-17': [
                    {
                        'staff_name': 'Bob Brown',
                        'staff_id': 4,
                        'position': 'Developer',
                        'schedule': ['WFH - Morning']
                    }
                ]
            }
        }

        # Assert the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected_response)

    @patch('view_schedule.invoke_http')  # Mock the invoke_http function
    @patch('view_schedule.db')  # Adjust the patch path accordingly
    def test_get_manager_schedule_error(self, mock_db, mock_invoke_http):
        # Mock the invoke_http response to return employee data
        mock_invoke_http.return_value = {
            "data": []
        }

        # Mock the database query to raise an exception
        mock_db.session.query.side_effect = Exception("Database connection error")

        # Make a GET request to the route
        response = self.client.get('/m_get_team_schedule/1')

        # Assert that the response is a 500 error
        self.assertEqual(response.status_code, 500)

        # Assert the error message is as expected
        expected_error_response = {
            "message": "An error occurred while retrieving the team schedule.",
            "error": "Database connection error"
        }
        self.assertEqual(response.json, expected_error_response)


class TestGetStaffSchedule(unittest.TestCase):
    # Set up the Flask test client
    def setUp(self):
        view_schedule_app.testing = True  # Set testing mode directly on the app
        self.client = view_schedule_app.test_client()  # Use the test client directly
        self.maxDiff = None

    @patch('view_schedule.invoke_http')  # Mock the invoke_http function
    @patch('view_schedule.db')  # Adjust the patch path accordingly
    def test_get_staff_schedule_success(self, mock_db, mock_invoke_http):
        # Mock the invoke_http response to return staff position and role
        mock_invoke_http.return_value = {
            "data": {
                "position": "Developer",
                "role": "Full-Time"
            }
        }

        # Mock the query results
        mock_query = MagicMock()
        mock_db.session.query.return_value = mock_query
        mock_query.join.return_value.join.return_value.filter.return_value.all.return_value = [
            (2, "Jane", "Smith", "IT", "Developer", datetime(2024, 10, 16), "Afternoon", "Pending Approval"),
            (4, "Bob", "Brown", "IT", "Developer", datetime(2024, 10, 17), "Morning", "Approved"),
            (2, "Jane", "Smith", "IT", "Developer", datetime(2024, 10, 17), "Afternoon", "Approved")
        ]

        # Make a GET request to the route
        response = self.client.get('/s_get_team_schedule/151408')

        # Define the expected response
        expected_response = {
            "IT": {
                "2024-10-16": [
                    {"staff_name": "Jane Smith", "staff_id": 2, "position": "Developer", "schedule": ["Pending - Afternoon"]}
                ],
                "2024-10-17": [
                    {"staff_name": "Bob Brown", "staff_id": 4, "position": "Developer", "schedule": ["WFH - Morning"]},
                    {"staff_name": "Jane Smith", "staff_id": 2, "position": "Developer", "schedule": ["WFH - Afternoon"]}
                ]
            }
        }

        # Assert the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected_response)

    @patch('view_schedule.db')  # Adjust the patch path accordingly
    def test_get_staff_schedule_error(self, mock_db):
        # Mock the database query to raise an exception
        mock_db.session.query.side_effect = Exception("Database connection error")

        # Make a GET request to the route
        response = self.client.get('/s_get_team_schedule/151408')

        # Assert that the response is a 500 error
        self.assertEqual(response.status_code, 500)
        
        # Assert the error message is as expected
        expected_error_response = {
            "message": "An error occurred while retrieving the staff schedule.",
            "error": "Database connection error"
        }
        self.assertEqual(response.json, expected_error_response)


if __name__ == '__main__':
    unittest.main()
