from flask import Flask, request, jsonify
import input_validation
from os import environ
import requests
from database import db, Request
from flask_cors import CORS
from invokes import invoke_http
from datetime import datetime


app = Flask(__name__)
app.config.from_object("config.Config")
CORS(app, resources={r"/*": {"origins": "*"}})
db.init_app(app)


request_URL = environ.get("REQUEST_URL") or "http://localhost:5001/request"
request_dates_URL = (
    environ.get("REQUEST_DATES_URL") or "http://localhost:5002/request_dates"
)
status_log_URL = environ.get("STATUS_LOG_URL") or "http://localhost:5003/status_log"


@app.route("/request/")
def hello():
    return "This is request.py"


# Create a new request
@app.route("/request/create", methods=["POST"])
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
        data = request.get_json()
        staff_id = data.get("staff_id")
        request_dates = data.get("request_dates")
        apply_reason = data.get("apply_reason")

        # Check if length of apply_reason is at most 100 characters
        if (
            input_validation.string_length_valid(
                input_string=apply_reason, max_length=100
            )
            == False
        ):
            return (
                jsonify(
                    {
                        "code": 400,
                        "error": "Your request reason is too long. Please keep it under 100 characters.",
                    }
                ),
                400,
            )

        # Check if length of all requested_shifts are at most 5 characters
        requested_shifts_concat_str = "".join(request_dates.values())
        number_of_requested_shifts = len(request_dates)
        if (
            input_validation.string_length_valid(
                input_string=requested_shifts_concat_str,
                max_length=(number_of_requested_shifts * 5),
            )
            == False
        ):
            return (
                jsonify(
                    {
                        "code": 400,
                        "error": "One or more of your requested shifts is too long. Please keep it under 5 characters.",
                    }
                ),
                400,
            )

        # Check if dates that staff requested for are within 2 months before and 3 months after current date
        earliest_requested_date = min(request_dates.keys())
        latest_requested_date = max(request_dates.keys())

        if (
            input_validation.check_date_valid(
                earliest_requested_date, latest_requested_date
            )
            == False
        ):
            return (
                jsonify(
                    {
                        "code": 400,
                        "error": "Your selected range of dates are not within 2 months before and 3 months after the current date.",
                    }
                ),
                400,
            )

        try:
            response = requests.get(
                f"{request_URL}/get_requests_by_staff_id/{staff_id}"
            )
            if response.status_code == 200:
                employee_requests = response.json()["data"]
            else:
                employee_requests = []
        except Exception as e:
            return (
                jsonify(
                    {
                        "code": 500,
                        "error": f"An error occurred while getting employee requests for staff_id {staff_id}: {e}",
                    }
                ),
                500,
            )

        existing_request_ids = [
            request_details["request_id"] for request_details in employee_requests
        ]

        # get all dates that staff has requested for from request_ids
        try:
            payload = {"request_ids": existing_request_ids}
            response = requests.post(
                f"{request_dates_URL}/get_by_request_ids", json=payload
            )
            if response.status_code == 200:
                requested_dates = response.json()["data"]
            else:
                requested_dates = []
        except Exception as e:
            return (
                jsonify(
                    {
                        "code": 500,
                        "error": f"An error occurred while getting employee requests for staff_id {staff_id}: {e}",
                    }
                ),
                500,
            )

        check_date = input_validation.has_existing_request(
            requested_dates, request_dates
        )

        if check_date != False:
            return (
                jsonify(
                    {
                        "code": 400,
                        "error": f"You have a duplicate request on {check_date}. Please check.",
                    }
                ),
                400,
            )

        # Create and commit the new request to get the request_id
        new_request = Request(
            staff_id=staff_id,
            creation_date=datetime.now().strftime("%Y-%m-%d"),
            apply_reason=apply_reason,
        )
        db.session.add(new_request)
        db.session.commit()

        try:
            add_request_dates = requests.post(
                f"{request_dates_URL}/create",
                json={
                    "request_id": new_request.request_id,
                    "request_dates": request_dates,
                    "staff_id": staff_id,
                },
            )

            if add_request_dates.status_code != 200:
                raise Exception("Failed to add request dates.")

        except Exception as e:
            # Compensating transaction: delete the previously committed request
            db.session.delete(new_request)
            db.session.commit()
            raise e

        # Log the action
        log_data = {
            "request_id": new_request.request_id,
            "action": "Request has been created by staff",
            "reason": apply_reason,
        }

        invoke_http(status_log_URL + "/add_event", json=log_data, method="POST")

        return (
            jsonify(
                {
                    "code": 200,
                    "message": "Request created successfully.",
                    "data": new_request.json(),
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "code": 500,
                    "error": f"An error occurred while creating the request. Details: {str(e)}",
                }
            ),
            500,
        )


# Get all requests
@app.route("/request/get_all_requests", methods=["GET"])
def get_all_requests():
    """
    Get all WFH requests
    ---
    Success response:
        {
            "code": 200,
            "data": [
                {
                    "request_id": 1,
                    "staff_id": 140894,
                    "creation_date": "2023-09-26",
                    "apply_reason": "Personal matters",
                    "reject_reason": null,
                },
                ...
            ]
        }
    """
    try:
        # Retrieve all requests from the database
        requests = Request.query.all()

        if requests:
            # Format the response
            request_list = [
                {
                    "request_id": request.request_id,
                    "staff_id": request.staff_id,
                    "creation_date": request.creation_date.isoformat(),
                    "apply_reason": request.apply_reason,
                    "reject_reason": request.reject_reason,
                }
                for request in requests
            ]

            return jsonify({"code": 200, "data": request_list})
        else:
            return jsonify({"code": 404, "error": "No requests found."}), 404

    except Exception as e:
        print("Error:", str(e))  # Debugging log
        return (
            jsonify(
                {
                    "code": 500,
                    "error": f"An error occurred while fetching the requests. Details: {str(e)}",
                }
            ),
            500,
        )


# Get all requests made by a staff_id
@app.route("/request/get_requests_by_staff_id/<int:staff_id>")
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
                    "creation_date": "2023-10-01",
                    "request_status": "Approved",
                    "manager_approval_date": "2023-10-01"
                },
                {
                    "request_id": 2,
                    "staff_id": 1,
                    "creation_date": "2023-10-02",
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
                {"code": 200, "data": [request.json() for request in requests]}
            )
        else:
            # If no requests are found for the given staff_id
            return (
                jsonify(
                    {
                        "code": 404,
                        "error": f"No requests found for staff_id: {staff_id}",
                    }
                ),
                404,
            )

    except Exception as e:
        # In case of an exception (e.g., database connection issues)
        return (
            jsonify(
                {
                    "code": 500,
                    "error": f"An error occurred while fetching the requests. Details: {str(e)}",
                }
            ),
            500,
        )


# Get request IDs made by a staff_id
@app.route("/request/get_request_ids/<int:staff_id>")
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
            return jsonify({"code": 200, "data": request_ids})
        else:
            # If no requests are found for the given staff_id
            return (
                jsonify(
                    {
                        "code": 404,
                        "data": [],
                        "error": f"No requests found for staff_id: {staff_id}",
                    }
                ),
                404,
            )

    except Exception as e:
        # In case of an exception (e.g., database connection issues)
        return (
            jsonify(
                {
                    "code": 500,
                    "error": f"An error occurred while fetching the request IDs. Details: {str(e)}",
                }
            ),
            500,
        )


# Add the reason if the request is rejected
@app.route("/request/update_reason", methods=["PUT"])
def update_reason():
    """
    Update "reason" field when the request is rejected
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
        request_id = request.json.get("request_id")

        request_record = Request.query.filter_by(request_id=request_id).first()

        if not request_record:
            return (
                jsonify(
                    {
                        "code": 404,
                        "message": f"No request found for request ID {request_id}.",
                    }
                ),
                404,
            )

        request_record.reject_reason = request.json.get("reason")

        # Commit the changes to the database
        db.session.commit()

        return (
            jsonify(
                {
                    "code": 200,
                    "message": f"Reason has been updated.",
                    "data": request_record.json(),
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "code": 500,
                    "error": "An error occurred while updating the reason. " + str(e),
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(port=5001, debug=True)
