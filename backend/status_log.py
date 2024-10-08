from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import input_validation
from os import environ
import requests
from request import db, Request
from flask_cors import CORS
from datetime import datetime


app = Flask(__name__)
app.config.from_object('config.Config')

# db = SQLAlchemy(app)
db.init_app(app)
CORS(app)


class StatusLog(db.Model):
    __tablename__ = "Status_Log"

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.Integer, db.ForeignKey('request.request_id'), nullable=False)
    log_date = db.Column(db.DateTime, default=datetime.utcnow)
    action = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.String(100), nullable=True)

    request = db.relationship("Request", backref="status_logs")

    def __init__(self, request_id, action, reason=None):
        self.request_id = request_id
        self.action = action
        self.reason = reason

    def json(self):
        return {
            "log_id": self.log_id,
            "request_id": self.request_id,
            "log_date": self.log_date.isoformat(),
            "action": self.action,
            "reason": self.reason,
        }


# Add event to the log
@app.route('/status_log/add_event', methods=['POST'])
def add_event():
    """
    Log a new status change event.
    ---
    Request body:
    {
        "request_id": <request_id>,
        "action": "<action>",
        "reason": "<reason>"
    }
    Success response:
    {
        "code": 201,
        "message": "Event logged successfully",
        "data": { ... }
    }
    """
    data = request.get_json()

    # Validate input data
    if not data or 'request_id' not in data or 'action' not in data:
        return jsonify({
            "code": 400,
            "error": "Invalid input. 'request_id' and 'action' are required."
        }), 400

    request_id = data['request_id']
    action = data['action']
    reason = data.get('reason')

    try:
        # Create a new StatusLog entry
        status_log = StatusLog(request_id=request_id, action=action, reason=reason)
        db.session.add(status_log)
        db.session.commit()

        return jsonify({
            "code": 201,
            "message": "Event logged successfully",
            "data": status_log.json()  # Return the logged status
        }), 201

    except Exception as e:
        print("Error:", str(e))  # Debugging log
        return jsonify({
            "code": 500,
            "error": "An error occurred while logging the event."
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)