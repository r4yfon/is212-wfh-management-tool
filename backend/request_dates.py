from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from request import db, Request
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('config.Config')
# db = SQLAlchemy(app)
db.init_app(app)
CORS(app)

# Defining the tables
# class Request(db.Model):
#     __tablename__ = "request"

#     request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     staff_id = db.Column(db.Integer, db.ForeignKey(
#         'employee.staff_id'), nullable=False)
#     request_date = db.Column(db.Date, nullable=False)
#     apply_reason = db.Column(db.String(100), nullable=False)
#     reject_reason = db.Column(db.String(100), nullable=True)

#     def __init__(self, staff_id, request_date, apply_reason, reject_reason=None, request_id=None):
#         self.request_id = request_id
#         self.staff_id = staff_id
#         self.request_date = request_date
#         self.apply_reason = apply_reason
#         self.reject_reason = reject_reason

#     def json(self):
#         return {
#             "request_id": self.request_id,
#             "staff_id": self.staff_id,
#             "request_date": self.request_date.isoformat(),
#             "apply_reason": self.apply_reason,
#             "reject_reason": self.reject_reason,
#         }


class RequestDates(db.Model):
    __tablename__ = "request_dates"

    request_date_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.Integer, db.ForeignKey(
        'request.request_id'), nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    request_shift = db.Column(db.String(5), nullable=False)
    request_status = db.Column(db.String(20), nullable=False)
    rescind_reason = db.Column(db.String(100), nullable=True)
    withdraw_reason = db.Column(db.String(100), nullable=True)

    def __init__(self, request_id, request_date, request_shift, request_date_id=None, request_status="Pending Approval", withdraw_reason=None, rescind_reason=None):
        self.request_date_id = request_date_id
        self.request_id = request_id
        self.request_date = request_date
        self.request_shift = request_shift
        self.request_status = request_status
        self.rescind_reason = rescind_reason
        self.withdraw_reason = withdraw_reason

    def json(self):
        return {
            "request_date_id": self.request_date_id,
            "request_id": self.request_id,
            "request_date": self.request_date.isoformat(),
            "request_shift": self.request_shift,
            "request_status": self.request_status,
            "withdraw_reason": self.withdraw_reason,
            "rescind_reason": self.rescind_reason,
        }


# Create
@app.route('/request_dates/create', methods=['POST'])
def create_request_dates():
    """
    Create a new request date
    ---
    Parameters (in JSON body):
        request_id (int): The request_id
        request_dates (dict): A dictionary with dates in YYYY-MM-DD format as keys and request shifts as values
            {
                "2024-09-24": "PM",
                "2024-09-25": "Full",
            }

    Success response:
        {
            "code": 201,
            "message": "Request dates created successfully.",
            "data": [
                {
                    "request_date_id": 1,
                    "request_id": 1,
                    "request_date": "2023-10-01",
                    "request_shift": "PM",
                    "request_status": "Pending"
                }
            ]
        }
    """
    try:
        data = request.get_json()
        request_id = data.get('request_id')
        request_dates = data.get('request_dates')

        if not request_id or not request_dates:
            return jsonify({
                "code": 400,
                "message": "Request ID or request dates not provided."
            }), 400

        # Check if the (foreign key constraint) request_id exists
        try:
            request_record = Request.query.filter_by(
                request_id=request_id).first()

            new_request_dates = []

            # Create new request dates
            with db.session.begin_nested():
                for request_date, request_shift in request_dates.items():
                    new_request_date = RequestDates(
                        request_id=request_id,
                        request_date=request_date,
                        request_shift=request_shift
                    )
                    db.session.add(new_request_date)
                    new_request_dates.append(new_request_date)

            db.session.commit()

            return jsonify({
                "code": 200,
                "message": "Request dates created successfully.",
                "data": [request_date.json() for request_date in new_request_dates]
            }), 200

        except Exception as e:
            # if not request_record:
            return jsonify({
                "code": 404,
                "message": f"No request found for request ID {request_id}: {e}"
            }), 404

        # new_request_dates = []

        # # Create new request dates
        # with db.session.begin_nested():
        #     for request_date, request_shift in request_dates.items():
        #         new_request_date = RequestDates(
        #             request_id=request_id,
        #             request_date=request_date,
        #             request_shift=request_shift
        #         )
        #         db.session.add(new_request_date)
        #         new_request_dates.append(new_request_date)

        # db.session.commit()

        # return jsonify({
        #     "code": 200,
        #     "message": "Request dates created successfully.",
        #     "data": [request_date.json() for request_date in new_request_dates]
        # }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "error": "An error occurred while creating the request dates. " + str(e)
        }),


# Retrieve
@app.route('/request_dates/get_by_request_id/<int:request_id>')
def get_request_dates(request_id):
    """
    Get request dates by request ID
    ---
    Parameters:
        request_id(int): The request_id

    Success response:
        {
            "code": 200,
            "data": [
                {
                    "request_date_id": 1,
                    "request_id": 1,
                    "request_date": "2023-10-01",
                    "request_shift": "PM",
                    "request_status": "Approved"
                }
            ]
        }
    """
    try:
        request_dates = RequestDates.query.filter_by(
            request_id=request_id).all()
        return jsonify(
            {
                "code": 200,
                "data": [request_date.json() for request_date in request_dates]
            }, 200
        )
    except Exception as e:
        return jsonify({
            "code": 404,
            "error": "Request dates not found. " + str(e)
        }), 404


@app.route('/request_dates/get_by_request_ids', methods=['POST'])
def get_request_dates_in_batch():
    """
    Get request dates by multiple request IDs in a list
    Parameters ( in request body):
        {
            "request_ids": [1, 2, 3]
        }
    ---
    Success response:
        {
            "code": 200,
            "data": [
                {
                    "request_date_id": 1,
                    "request_id": 1,
                    "request_date": "2023-10-01",
                    "request_shift": "PM",
                    "request_status": "Approved"
                },
                {
                    "request_date_id": 2,
                    "request_id": 2,
                    "request_date": "2023-10-02",
                    "request_shift": "PM",
                    "request_status": "Approved"
                }
            ]
        }
    """

    try:
        request_id_list = request.json.get('request_ids', [])
        if not request_id_list:
            return jsonify({
                "code": 400,
                "message": "No request IDs provided."
            }), 400

        # Get all the request dates for the given request_ids
        request_dates = RequestDates.query.filter(
            RequestDates.request_id.in_(request_id_list)).all()
        return jsonify(
            {
                "code": 200,
                "data": [request_date.json() for request_date in request_dates]
            }
        ), 200
    except Exception as e:
        return jsonify({
            "code": 404,
            "error": "Request dates not found. " + str(e)
        }), 404


# Change status to all the records that belongs to the same request_id
@app.route('/request_dates/change_all_status', methods=['PUT'])
def change_all_status():
    try:
        # Get request data
        request_id = request.json.get('request_id')
        new_status = request.json.get('status')

        # Check if the necessary data is provided
        if not request_id or not new_status:
            return jsonify({
                "code": 400,
                "message": "Request ID or status not provided."
            }), 400

        # Query the request dates by request_id
        request_dates = RequestDates.query.filter_by(
            request_id=request_id).all()

        if not request_dates:
            return jsonify({
                "code": 404,
                "message": f"No request dates found for request ID {request_id}."
            }), 404

        # Update the Request_Status for each record
        for request_date in request_dates:
            if request_date.request_status != "Withdrawn" and request_date.request_status != "Pending Withdrawal":
                request_date.request_status = new_status

                # If the new status is 'pending_rescind', update the Rescind_Reason
                if new_status == "Rescinded":
                    if not request.json.get('reason'):
                        return jsonify({
                            "code": 400,
                            "message": "Rescind reason must be provided."
                        }), 400
                    request_date.rescind_reason = request.json.get('reason')

                # If the new status is 'withdraw', update the Withdraw_Reason
                if new_status == "Withdrawn" or new_status == "Pending Withdrawal":
                    if not request.json.get('reason'):
                        return jsonify({
                            "code": 400,
                            "message": "Withdraw reason must be provided."
                        }), 400
                    request_date.withdraw_reason = request.json.get('reason')

        # Commit the changes to the database
        db.session.commit()

        return jsonify({
            "code": 200,
            "message": f"Request status for request ID {request_id} updated to {new_status}.",
            "data": [request_date.json() for request_date in request_dates]
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "error": "An error occurred while updating the request status. " + str(e)
        }), 500


# Withdraw or rescind some of the dates in a request
@app.route('/request_dates/change_partial_status', methods=['PUT'])
def change_partial_status():
    try:
        # Get request data from JSON body
        request_id = request.json.get('request_id')
        new_status = request.json.get('status')
        reason = request.json.get('reason')
        dates = request.json.get('dates')

        # Check if all necessary data is provided
        if not request_id or not new_status or not dates:
            return jsonify({
                "code": 400,
                "message": "Request ID, status, and dates must be provided."
            }), 400

        # Query the request dates that match the request_id and are in the provided dates list
        request_dates = RequestDates.query.filter(
            RequestDates.request_id == request_id,
            RequestDates.request_date.in_(dates)
        ).all()

        if not request_dates:
            return jsonify({
                "code": 404,
                "message": f"No request dates found for request ID {request_id} and provided dates."
            }), 404

        # Update the Request_Status and Reason for each matching record
        for request_date in request_dates:
            request_date.request_status = new_status

            # Update the reason based on the status
            if new_status == "Rescinded":
                if not reason:
                    return jsonify({
                        "code": 400,
                        "message": "Rescind reason must be provided."
                    }), 400
                request_date.rescind_reason = reason
            elif new_status == "Withdrawn" or new_status == "Pending Withdrawal":
                if not reason:
                    return jsonify({
                        "code": 400,
                        "message": "Withdraw reason must be provided."
                    }), 400
                request_date.withdraw_reason = reason

        # Commit the changes to the database
        db.session.commit()

        # Format the updated records for the response
        updated_dates = [request_date.json() for request_date in request_dates]

        return jsonify({
            "code": 200,
            "message": f"Request status for request ID {request_id} updated to {new_status} for the provided dates.",
            "data": updated_dates
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "error": f"An error occurred while updating the request status: {str(e)}"
        }), 500


# get staff's pending and approved pending withdrawal requests
@app.route('/request_dates/get_staff_request/<int:request_id>')
def get_staff_request(request_id):
    """
    Get request dates by request ID
    ---
    Parameters:
        request_id(int): The request_id

    Success response:
        {
            "code": 200,
            "data": [
                {
                    "request_date_id": 1,
                    "request_id": 1,
                    "request_date": "2023-10-01",
                    "request_shift": "PM",
                    "request_status": "Approved"
                }
            ]
        }
    """
    try:
        request_dates = RequestDates.query.filter(
            (RequestDates.request_id == request_id) &
            (RequestDates.request_status.in_(
                ["Pending Approval", "Pending Withdrawal"]))
        ).all()

        if not request_dates:
            return jsonify({
                "code": 404,
                "error": "No request dates found with the specified status."
            }), 404

        return jsonify(
            {
                "code": 200,
                "data": [request_date.json() for request_date in request_dates]
            }, 200
        )
    except Exception as e:
        return jsonify({
            "code": 500,
            "error": "An error occurred while retrieving request dates. " + str(e)
        }), 500


@app.route('/request_dates/auto_reject', methods=['PUT'])
def auto_reject():
    from datetime import datetime, timedelta
    # Get today's date
    today = datetime.today()
    
    # Calculate the date 2 months ago from today
    two_months_ago = today - timedelta(days=60)
    
    # Query all records with status 'Pending'
    pending_requests = RequestDates.query.filter_by(request_status='Pending Approval').all()
    
    updated_requests = []
    
    # Iterate through pending requests and check the request_date
    for request in pending_requests:
        if request.request_date < two_months_ago.date():
            # Update the status to 'Rejected'
            request.request_status = 'Rejected'
            updated_requests.append(request)
    
    # Commit the changes to the database
    db.session.commit()

    return jsonify({
        'message': f'{len(updated_requests)} requests have been updated to Rejected',
        'updated_requests': [{'id': req.request_id, 'request_date': req.request_date, 'new_status': req.request_status} for req in updated_requests]
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
