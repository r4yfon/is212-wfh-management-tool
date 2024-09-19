from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from input_validation import string_length_valid
from os import environ
import requests

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)


class Employee(db.Model):
    __tablename__ = "employee"

    staff_id = db.Column(db.Integer, primary_key=True)
    staff_fname = db.Column(db.String(50), nullable=False)
    staff_lname = db.Column(db.String(50), nullable=False)
    dept = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    reporting_manager = db.Column(
        db.Integer, db.ForeignKey('employee.staff_id'), nullable=True)
    role = db.Column(db.Integer, nullable=False)

    def __init__(self, staff_id, staff_fname, staff_lname, dept, position, country, email, role, reporting_manager=None):
        self.staff_id = staff_id
        self.staff_fname = staff_fname
        self.staff_lname = staff_lname
        self.dept = dept
        self.position = position
        self.country = country
        self.email = email
        self.reporting_manager = reporting_manager
        self.role = role

    def json(self):
        return {
            "staff_id": self.staff_id,
            "staff_fname": self.staff_fname,
            "staff_lname": self.staff_lname,
            "dept": self.dept,
            "position": self.position,
            "country": self.country,
            "email": self.email,
            "reporting_manager": self.reporting_manager,
            "role": self.role
        }


class Request(db.Model):
    __tablename__ = "request"

    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    staff_id = db.Column(db.Integer, db.ForeignKey(
        'employee.staff_id'), nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    apply_reason = db.Column(db.String(100), nullable=False)
    reject_reason = db.Column(db.String(100), nullable=True)

    def __init__(self, staff_id, request_date, apply_reason, reject_reason=None, request_id=None):
        self.request_id = request_id
        self.staff_id = staff_id
        self.request_date = request_date
        self.apply_reason = apply_reason
        self.reject_reason = reject_reason

    def json(self):
        return {
            "request_id": self.request_id,
            "staff_id": self.staff_id,
            "request_date": self.request_date.isoformat(),
            "apply_reason": self.apply_reason,
            "reject_reason": self.reject_reason,
        }


request_dates_URL = environ.get(
    'request_dates_URL') or "http://localhost:5002/request_dates"

# Create a new request


@app.route('/request/create', methods=['POST'])
def create_request():
    """
    Create a new request
    ---
    Parameters (in JSON body):
        staff_id (int): The staff_id
        request_date (str): The date that staff sent this request in YYYY-MM-DD format
        request_dates (dict): A dictionary with dates in YYYY-MM-DD format as keys and request shifts as values
            {
                "2024-09-24": "PM",
                "2024-09-25": "Full",
            }
        apply_reason (str): The reason for the request

    Success response:
        {
            "code": 201,
            "message": "Request created successfully.",
            "data": {
                "request_id": 1,
                "staff_id": 1,
                "request_date": "2023-10-01",
                "request_dates": ["2023-10-01", "2023-10-02"],
                "apply_reason": "Reason for request"
            }
        }
    """
    try:
        data = request.get_json()
        staff_id = data.get('staff_id')
        request_date = data.get('request_date')
        request_dates = data.get('request_dates')
        apply_reason = data.get('apply_reason')

        # Check if length of apply_reason is at most 100 characters
        if not string_length_valid(input_string=apply_reason, max_length=100):
            return jsonify({
                "code": 400,
                "error": "Your request reason is too long. Please keep it under 100 characters."
            })

        # Check if length of all requested_shifts are at most 5 characters
        # Not sure if needed, assuming requested_shifts will be radio buttons for frontend TODO: check with frontend
        # requested_shifts_concat_str = ''.join(request_dates.values())
        # number_of_requested_shifts = len(request_dates)
        # if not string_length_valid(input_string=requested_shifts_concat_str, max_length=(number_of_requested_shifts * 5)):
        #     return jsonify({
        #         "code": 400,
        #         "error": "One of more of your requested shifts is too long. Please keep it under 5 characters."
        #     })

        # TODO: check if staff already has a request for the same date

        new_request = Request(
            staff_id=staff_id,
            request_date=request_date,
            apply_reason=apply_reason
        )

        # TODO: need the request's request_id, then send request_dates with request_id to RequestDates table
        create_request_dates = requests.post(f'{request_dates_URL}/create', json={
            "request_id": new_request.request_id,
            "request_dates": request_dates
        })

        if create_request_dates.status_code == 200:
            db.session.add(new_request)
            db.session.commit()

            return jsonify({
                "code": 200,
                "message": "Request created successfully. Sending requested dates to RequestDates table.",
                "data": new_request.json()
            }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "error": f"An error occurred while creating the request. Details: {str(e)}"
        }), 500


# Get all requests made by a staff_id
@app.route('/request/get_all_requests/<int:staff_id>')
def get_requests_by_staff_id(staff_id):
    """
    Get all requests by staff id
    ---
    Parameters:
        staff_id (int): The staff_id

    Success response:
        {
            "code": 200,
            "data": [
                {
                    "request_id": 1,
                    "staff_id": 1,
                    "request_date": "2023-10-01",
                    "request_status": "Approved",
                    "manager_approval_date": "2023-10-01"
                },
                {
                    "request_id": 2,
                    "staff_id": 1,
                    "request_date": "2023-10-02",
                    "request_status": "Approved",
                    "manager_approval_date": "2023-10-02"
                }
            ]
        }
    """

    try:
        requests = Request.query.filter_by(staff_id=staff_id).all()
        if requests:
            # Return a list of all requests
            return jsonify(
                {
                    "code": 200,
                    "data": [request.json() for request in requests]
                }
            )
        else:
            # If no requests are found for the given staff_id
            return jsonify({
                "code": 404,
                "error": f"No requests found for staff_id: {staff_id}"
            }), 404

    except Exception as e:
        # In case of an exception (e.g., database connection issues)
        return jsonify({
            "code": 500,
            "error": f"An error occurred while fetching the requests. Details: {str(e)}"
        }), 500


# Get request IDs made by a staff_id
@app.route('/request/get_request_ids/<int:staff_id>')
def get_request_ids_by_staff_id(staff_id):
    """
    Get request IDs by staff id
    ---
    Parameters:
        staff_id (int): The staff_id

    Success response:
        {
            "code": 200,
            "data": [1, 2, 3]
        }
    """

    try:
        requests = Request.query.filter_by(staff_id=staff_id).all()
        if requests:
            # Return a list of request IDs
            request_ids = [request.request_id for request in requests]
            return jsonify(
                {
                    "code": 200,
                    "data": request_ids
                }
            )
        else:
            # If no requests are found for the given staff_id
            return jsonify({
                "code": 404,
                "error": f"No requests found for staff_id: {staff_id}"
            }), 404

    except Exception as e:
        # In case of an exception (e.g., database connection issues)
        return jsonify({
            "code": 500,
            "error": f"An error occurred while fetching the request IDs. Details: {str(e)}"
        }), 500


# Add the reason if the request is rejected, withdrawn or cancelled
@app.route('/request/update_reason', methods=['PUT'])
def update_reason():
    """
    Update "reason" field when the request is rejected, withdrawn or cancelled
    ---
    Parameters:
        request_id (int): The request ID
        status (str): The status of the request
        reason (str): The reason for the status change

    Success response:
        {
            "code": 200,
            "message": "Reason has been updated.",
            "data": {
                "request_id": 1,
                "staff_id": 1,
                "request_date": "2023-10-01",
                "request_status": "Approved",
                "manager_approval_date": "2023-10-01"
            }
        }
    """
    try:
        # Get request data from the request body
        request_id = request.json.get('request_id')
        new_status = request.json.get('status')

        request_record = Request.query.filter_by(request_id=request_id).first()

        if not request_record:
            return jsonify({
                "code": 404,
                "message": f"No request found for request ID {request_id}."
            }), 404

        if new_status == "Pending Withdrawal":
            request_record.withdraw_reason = request.json.get('reason')

        if new_status == "Pending Cancellation":
            request_record.cancel_reason = request.json.get('reason')

        if new_status == "Rejected":
            request_record.reject_reason = request.json.get('reason')

        # Commit the changes to the database
        db.session.commit()

        return jsonify({
            "code": 200,
            "message": f"Reason has been updated.",
            "data": request_record.json()
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "error": "An error occurred while updating the reason. " + str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
