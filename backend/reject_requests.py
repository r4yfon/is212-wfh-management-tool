from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from invokes import invoke_http
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
CORS(app)

#######################################################
staff_id = "150488"

# Staff view own requests
@app.route("/reject_request", methods=['PUT'])
def reject_request():
    try:
        # Retrieve data from the request body
        request_id = request.json.get('request_id')
        reason = request.json.get('reason')

        if not request_id or not reason:
            return jsonify({
                "code": 400,
                "message": "Request ID or reason not provided."
            }), 400

        data = {
            "request_id": request_id,
            "reason": reason,
            "status": "Rejected"
        }

        # Invoke the API to update the reason for rejection
        update_reason_response = invoke_http("http://localhost:5001/request/update_reason", json=data, method='PUT')

        if update_reason_response.get('code') != 200:
            return jsonify({
                "code": update_reason_response.get('code', 500),
                "message": update_reason_response.get('message', 'Failed to update reason for request.')
            }), update_reason_response.get('code', 500)

        # Invoke the API to change the status of all records with the same request_id
        change_status_response = invoke_http("http://localhost:5002/request_dates/change_all_status", json=data, method='PUT')

        if change_status_response.get('code') != 200:
            return jsonify({
                "code": change_status_response.get('code', 500),
                "message": change_status_response.get('message', 'Failed to update the status for the related request dates.')
            }), change_status_response.get('code', 500)

        # If both requests are successful
        return jsonify({
            "code": 200,
            "message": "Request rejection reason and status updated successfully.",
            "data": {
                "update_reason_response": update_reason_response,
                "change_status_response": change_status_response
            }
        }), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            "code": 500,
            "message": "An unexpected error occurred: " + str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5102, debug=True)