from flask import Flask, request, jsonify
import requests
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime, timedelta
from request import Request
from request_dates import RequestDates
from input_validation import check_date_valid
from flask_cors import CORS
from invokes import invoke_http

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
CORS(app, resources={r"/view_schedule/weekly/*": {"origins": "*"}})

employee_URL = environ.get(
    'employee_URL') or "http://localhost:5000/employee"
request_URL = environ.get(
    'request_URL') or "http://localhost:5001/request"
request_dates_URL = environ.get(
    'request_dates_URL') or "http://localhost:5002/request_dates"

def get_week_from_date(date_entered):
    """
    Get the start and end dates of the week based on the date_entered. By default, week starts on Monday and ends on Sunday, so we change it to be from Sunday to Monday.
    ---
    Parameters:
        date_entered (string): The date in the format YYYY-MM-DD

    Returns:
        tuple(
            start_date (date): Start date of the week,
            end_date (date): End date of the week
        )
    """
    date_entered = datetime.strptime(date_entered, '%Y-%m-%d').date()
    start_date = date_entered - \
        timedelta(days=(date_entered.weekday() + 1) % 7)
    end_date = start_date + timedelta(days=6)

    return start_date, end_date


@app.route("/view_schedule/weekly/<int:staff_id>/<string:date_entered>")
def view_weekly_schedule(staff_id, date_entered):
    """
    View weekly schedule based on staff_id and date entered
    ---
    Parameters:
        staff_id (int): The ID of the staff
        date_entered (string): The date in the format YYYY-MM-DD

    Success response:
            Weekly schedule for the given staff. The week is calculated based on the date_entered. It will be in a dictionary, where the keys are the dates and the values are the location and shift (if applicable).

            Example:
            {
                "2023-10-01": ["WFH - PM"],
                "2023-10-02": ["Office", "Pending: WFH - PM"],
                "2023-10-03": ["Office", "Pending: WFH - Full"],
                "2023-10-04": ["Office"],
                "2023-10-05": ["Office"],
                "2023-10-06": ["Office"],
                "2023-10-07": ["Office"],
            }
    """

    # check if date_entered is within 2 months back, 3 month forward (OVS06)
    if not check_date_valid(date_entered, date_entered):
        return jsonify({
            "code": 400,
            "message": "Date entered is not within 2 months back and 3 months forward."
        }), 400

    week_start, week_end = get_week_from_date(date_entered)
    weekly_arrangement = {}
    for n in range((week_end - week_start).days + 1):
        weekly_arrangement[str(week_start + timedelta(days=n))] = ["Office"]

    # Query the requests submitted by the staff_id
    try:
        # This will get all the WFH requests made by the staff_id; check documentation in parent file for details
        all_request_ids = requests.get(
            f'{request_URL}/get_request_ids/{int(staff_id)}').json()['data']

        results = db.session.query(Request, RequestDates).join(
            RequestDates, Request.request_id == RequestDates.request_id
        ).filter(
            Request.request_id.in_(all_request_ids)
        ).all()

        # Create a response structure
        requests_in_request_id = []
        for req, req_date in results:
            requests_in_request_id.append({
                "request_id": req.request_id,
                "staff_id": req.staff_id,
                "request_submission_date": req.creation_date,
                "request_date": req_date.request_date.isoformat(),
                "request_shift": req_date.request_shift,
                "request_status": req_date.request_status
            })

        for request_info in requests_in_request_id:
            request_date = datetime.strptime(
                request_info['request_date'], '%Y-%m-%d').date()
            if week_start <= request_date <= week_end:
                if request_info['request_status'] == 'Approved':
                    weekly_arrangement[str(
                        request_date)] = [f'WFH - {request_info["request_shift"]}']
                elif request_info['request_status'] == 'Pending Withdrawal':
                    weekly_arrangement[str(
                        request_date)] = [f'Home - {request_info["request_shift"]}', "Pending: Office"]
                elif request_info['request_status'] == 'Pending Approval':
                    weekly_arrangement[str(
                        request_date)] = ["Office", f'Pending: WFH - {request_info["request_shift"]}']

        return jsonify({
            "code": 200,
            "data": weekly_arrangement,
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to fetch requests: {str(e)}"}), 500


# Get organisation schedule
@app.route("/get_org_schedule", methods=['GET'])
def get_org_schedule():
    # Get all requests made by the staff_id
    request_response = invoke_http(request_URL + "/get_all_requests", method='GET')
    
    if request_response["code"] == 200:
        request_list = []
        for request in request_response["data"]:
            request_dict = {"staff_id": request["staff_id"], "staff_name": request["staff_id"], "request_id": request["request_id"], "request_dates": []}
            
            staff_request_dates = invoke_http(request_dates_URL + "/get_by_request_id/" + str(request["request_id"]), method='GET')
            for request_dates in staff_request_dates[0]["data"]:
                if request_dates["request_status"] == "Pending Approval" or request_dates["request_status"] == "Approved":
                    request_dict["request_dates"].append({request_dates["request_date"]: request_dates["request_shift"]})
                    request_dict["request_status"] = request_dates["request_status"]
            if len(request_dict["request_dates"]) > 0:
                request_list.append(request_dict)
    
    # Return the modified response including the request_dates
    return jsonify(request_list)


# Get team schedule
@app.route("/get_team_schedule/<int:staff_id>", methods=['GET'])
def get_team_schedule(staff_id):
    # Get all requests made by the staff_id
    response = invoke_http(employee_URL + "/get_all_employees", method='GET')

    def get_team_members(staff_id, visited=None, staff_details=None):
        # Initialize visited set to track processed staff_ids
        if visited is None:
            visited = set()
        if staff_details is None:
            staff_details = {}

        # Prevent recursion if the staff_id has already been processed
        if staff_id in visited:
            return staff_details

        # Mark this staff_id as visited
        visited.add(staff_id)

        # Iterate through each member in the response data
        for member in response["data"]:
            if member["reporting_manager"] == staff_id:
                # Add the current member's details to the staff_details dictionary
                staff_details[member["staff_id"]] = {
                    "staff_name": member["staff_name"],
                    "dept": member["dept"],
                    "position": member["position"]
                }

                # Recursively find team members under the current member
                staff_details.update(get_team_members(member["staff_id"], visited, staff_details))

        return staff_details

    # Get the full list of team members under the given staff_id
    all_team_members = get_team_members(staff_id)

    request_response = invoke_http(request_URL + "/get_all_requests", method='GET')
    
    if request_response["code"] == 200:
        request_list = []
        for request in request_response["data"]:
            if request["staff_id"] in all_team_members.keys():
                request_dict = {"staff_id": request["staff_id"], "staff_name": all_team_members[request["staff_id"]]["staff_name"], "request_id": request["request_id"], "request_dates": []}
                
                staff_request_dates = invoke_http(request_dates_URL + "/get_by_request_id/" + str(request["request_id"]), method='GET')
                for request_dates in staff_request_dates[0]["data"]:
                    if request_dates["request_status"] == "Pending Approval" or request_dates["request_status"] == "Approved":
                        request_dict["request_dates"].append({request_dates["request_date"]: request_dates["request_shift"]})
                        request_dict["request_status"] = request_dates["request_status"]
                if len(request_dict["request_dates"]) > 0:
                    request_list.append(request_dict)

    return jsonify({
        "code": 200,
        "data": request_list
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)
