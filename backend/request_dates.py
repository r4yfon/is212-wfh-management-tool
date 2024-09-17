from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get(
    'dbURL') or 'mysql+mysqlconnector://root:root@localhost:3306/wfh_scheduling'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)
CORS(app, resources={r"/*": {"origins": "*"}})


class RequestDates(db.Model):
    __tablename__ = "request_dates"

    request_date_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.Integer, db.ForeignKey(
        'request.request_id'), nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    request_shift = db.Column(db.String(5), nullable=False)
    request_status = db.Column(db.String(20), nullable=False)

    def __init__(self, request_id, request_date, request_status, request_shift):
        self.request_id = request_id
        self.request_date = request_date
        self.request_shift = request_shift
        self.request_status = request_status

    def json(self):
        return {
            "request_date_id": self.request_date_id,
            "request_id": self.request_id,
            "request_date": self.request_date.isoformat(),
            "request_shift": self.request_shift,
            "request_status": self.request_status
        }


@app.route('/get_request_dates_by_request_id/<int:request_id>')
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


@app.route('/get_request_dates_by_request_ids', methods=['POST'])
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
