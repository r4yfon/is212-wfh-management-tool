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


class Request(db.Model):
    __tablename__ = "request"

    request_id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey(
        'employee.staff_id'), nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    request_status = db.Column(db.String(20), nullable=False)
    manager_approval_date = db.Column(db.Date, nullable=True)

    def __init__(self, request_id, staff_id, request_date, request_status, manager_approval_date=None):
        self.request_id = request_id
        self.staff_id = staff_id
        self.request_date = request_date
        self.request_status = request_status
        self.manager_approval_date = manager_approval_date

    def json(self):
        return {
            "request_id": self.request_id,
            "staff_id": self.staff_id,
            "request_date": self.request_date.isoformat(),
            "request_status": self.request_status,
            "manager_approval_date": self.manager_approval_date
        }


@app.route('/get_all_requests/<int:staff_id>')
def get_requests_by_staff_id(staff_id):
    """
    Get all requests by staff id
    ---
    responses:
        200:
            description: Return all requests
        404:
            description: Unable to find requests
    """
    try:
        requests = Request.query.filter_by(staff_id=staff_id).all()
        return jsonify(
            {
                "code": 200,
                "data": [request.json() for request in requests]
            }
        )

    except Exception as e:
        return jsonify({
            "code": 404,
            "error": "Requests not found. " + str(e)
        }), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
