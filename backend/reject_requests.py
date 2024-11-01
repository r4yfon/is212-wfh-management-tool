from flask import request, jsonify, Blueprint
from invokes import invoke_http
from flask_cors import CORS
from os import environ

app = Blueprint("reject_requests", __name__)
CORS(app)

request_URL = environ.get("REQUEST_URL") or "http://localhost:5001/request"
request_dates_URL = (
    environ.get("REQUEST_DATES_URL") or "http://localhost:5002/request_dates"
)
status_log_URL = environ.get("STATUS_LOG_URL") or "http://localhost:5003/status_log"


@app.route("/")
def hello():
    return "This is reject_requests.py"


# Rejects request
@app.route("/reject_request", methods=["PUT"])
def reject_request():
    """
    Manager rejects a request
    ---
    Parameters (in JSON body):
        {
            "request_id": 1,
            "reason": "Insufficient justification for the leave"
        }

    Success response:
        {
            "code": 200,
            "message": "Request created successfully.",
            "data": {
                "request_id": 1,
                "staff_id": 1,
                "creation_date": "2023-10-01",
                "request_dates": ["2023-10-01", "2023-10-02"],
                "apply_reason": "Reason for request"
            }
        }
    """
    try:
        # Retrieve data from the request body
        request_id = request.json.get("request_id")
        reason = request.json.get("reason")

        if not request_id or not reason:
            return (
                jsonify({"code": 400, "message": "Request ID or reason not provided."}),
                400,
            )

        data = {"request_id": request_id, "reason": reason, "status": "Rejected"}

        # Invoke the API to update the reason for rejection
        update_reason_response = invoke_http(
            request_URL + "/update_reason", json=data, method="PUT"
        )

        if update_reason_response.get("code") != 200:
            return jsonify(
                {
                    "code": update_reason_response.get("code", 500),
                    "message": update_reason_response.get(
                        "message", "Failed to update reason for request."
                    ),
                }
            ), update_reason_response.get("code", 500)

        # Invoke the API to change the status of all records with the same request_id
        change_status_response = invoke_http(
            request_dates_URL + "/change_all_status", json=data, method="PUT"
        )

        if change_status_response.get("code") != 200:
            return jsonify(
                {
                    "code": change_status_response.get("code", 500),
                    "message": change_status_response.get(
                        "message",
                        "Failed to update the status for the related request dates.",
                    ),
                }
            ), change_status_response.get("code", 500)

        log_data = {
            "request_id": request_id,
            "action": "Request has been rejected by the manager/director",
            "reason": reason,
        }

        invoke_http(status_log_URL + "/add_event", json=log_data, method="POST")

        # If both requests are successful
        return (
            jsonify(
                {
                    "code": 200,
                    "message": "Request rejection reason and status updated successfully.",
                    "data": {
                        "update_reason_response": update_reason_response,
                        "change_status_response": change_status_response,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        # Handle unexpected errors
        return (
            jsonify(
                {"code": 500, "message": "An unexpected error occurred: " + str(e)}
            ),
            500,
        )


# if __name__ == "__main__":
#     app.run()
