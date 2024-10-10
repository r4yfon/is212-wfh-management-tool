import unittest
import flask_testing
from request_dates import app, db, RequestDates
from employee import db as employee_db, Employee
from request import db as request_db, Request
from request_dates import db as request_dates_db, RequestDates
from status_log import db as status_log_db, StatusLog

from datetime import date

class TestApp(flask_testing.TestCase):
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
    app.config['TESTING'] = True

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()

        # Create a test employee object
        test_employee = Employee(
            staff_id=150488,
            staff_fname='Jacob',
            staff_lname='Tan',
            dept='Engineering',
            position='Call Centre',
            country='Singapore',
            email='Jacob.Tan@allinone.com.sg',
            role=2,
            reporting_manager=None
        )
        employee_db.session.add(test_employee)
        employee_db.session.commit()

        # Now add a test request
        test_request = Request(
            request_id=100,
            staff_id=150488,
            creation_date=date(2024, 10, 10),
            apply_reason='WFH',
            reject_reason=None
        )
        request_db.session.add(test_request)
        request_db.session.commit()

        # Add test data for the request_dates table
        request_date1 = RequestDates(
            request_id=100,
            request_date=date(2024, 10, 17),
            request_shift='PM',
            request_status='Approved'
        )
        request_dates_db.session.add(request_date1)
        request_dates_db.session.commit()


    def tearDown(self):
        db.session.remove()
        db.drop_all()

class TestGetRequestDates(TestApp):
    def test_get_request_dates_success(self):
        # Call the endpoint
        response = self.client.get("/request_dates/get_by_request_id/100",
                                    content_type='application/json')
        # Assert the response
        expected_response = [{'code': 200, 'data': [{'request_date': '2024-10-17', 'request_date_id': 1, 'request_id': 100, 'request_shift': 'PM', 'request_status': 'Approved', 'rescind_reason': None, 'withdraw_reason': None}]}, 200]
        self.assertEqual(response.get_json(), expected_response)

    def test_get_request_dates_failure(self):
        # Call the endpoint
        response = self.client.get("/request_dates/get_by_request_id/1213",
                                    content_type='application/json')
        # Assert the response
        expected_response = [
            {
                "code": 200,
                "data": []
            },
            200
        ]
        self.assertEqual(response.get_json(), expected_response)

if __name__ == '__main__':
    unittest.main()
