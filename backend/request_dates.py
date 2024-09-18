from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)


class Request(db.Model):
    __tablename__ = "request"

    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    staff_id = db.Column(db.Integer, db.ForeignKey(
        'employee.staff_id'), nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    request_shift = db.Column(db.String(5), nullable=False)
    request_status = db.Column(db.String(20), nullable=False)
    rescind_reason = db.Column(db.String(100), nullable=True)
    withdraw_reason = db.Column(db.String(100), nullable=True)

    def __init__(self, request_id, staff_id, request_date, request_shift, request_status, rescind_reason=None, withdraw_reason=None):
        self.request_id = request_id
        self.staff_id = staff_id
        self.request_date = request_date
        self.request_shift = request_shift
        self.request_status = request_status
        self.rescind_reason = rescind_reason
        self.withdraw_reason = withdraw_reason

    def json(self):
        return {
            "request_id": self.request_id,
            "staff_id": self.staff_id,
            "request_date": self.request_date.isoformat(),
            "request_shift": self.request_shift,
            "request_status": self.request_status,
            "rescind_reason": self.rescind_reason,
            "withdraw_reason": self.withdraw_reason
        }


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

    def __init__(self, request_date_id, request_id, request_date, request_status, request_shift, rescind_reason=None, withdraw_reason=None):
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
            "rescind_reason": self.rescind_reason,
            "withdraw_reason": self.withdraw_reason
        }


@app.route('/request_dates/get_request_dates_by_request_id/<int:request_id>')
def get_request_dates(request_id):
    """
    Get request dates by request ID
    ---
    Parameters:
        request_id (int): The request_id

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
            }
        )
    except Exception as e:
        return jsonify({
            "code": 404,
            "error": "Request dates not found. " + str(e)
        }), 404


@app.route('/request_dates/get_request_dates_by_request_ids', methods=['POST'])
def get_request_dates_in_batch():
    """
    Get request dates by multiple request IDs in a list
    Parameters (in request body):
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
        )
    except Exception as e:
        return jsonify({
            "code": 404,
            "error": "Request dates not found. " + str(e)
        }), 404


# Change status to all the records that belongs to the same request_id
@app.route('/request_dates/change_status', methods=['PUT'])
def change_status():

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
            request_date.request_status = new_status

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
