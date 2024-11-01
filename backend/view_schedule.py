from flask import jsonify, Blueprint
import requests
from os import environ
from datetime import datetime, timedelta
from request import Request
from employee import Employee
from request_dates import RequestDates
from input_validation import check_date_valid
from flask_cors import CORS
from invokes import invoke_http
from datetime import datetime, timedelta
from sqlalchemy import func
from run import db

app = Blueprint("view_schedule", __name__)
CORS(app, resources={r"/*": {"origins": "*"}})

employee_URL = environ.get("EMPLOYEE_URL") or "http://localhost:5000/employee"
request_URL = environ.get("REQUEST_URL") or "http://localhost:5001/request"
request_dates_URL = (
    environ.get("REQUEST_DATES_URL") or "http://localhost:5002/request_dates"
)


@app.route("/")
def hello():
    return "This is view_schedule.py"


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
    date_entered = datetime.strptime(date_entered, "%Y-%m-%d").date()
    start_date = date_entered - timedelta(days=(date_entered.weekday() + 1) % 7)
    end_date = start_date + timedelta(days=6)

    return start_date, end_date


@app.route("/weekly/<int:staff_id>/<string:date_entered>")
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
            "code": 200,
            "data": {
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
        return (
            jsonify(
                {
                    "code": 400,
                    "message": "Date entered is not within 2 months back and 3 months forward.",
                }
            ),
            400,
        )

    week_start, week_end = get_week_from_date(date_entered)
    weekly_arrangement = {}
    for n in range((week_end - week_start).days + 1):
        weekly_arrangement[str(week_start + timedelta(days=n))] = ["Office"]

    # Query the requests submitted by the staff_id
    try:
        # This will get all the WFH requests made by the staff_id; check documentation in parent file for details
        all_request_ids = requests.get(
            f"{request_URL}/get_request_ids/{int(staff_id)}"
        ).json()["data"]

        results = (
            db.session.query(Request, RequestDates)
            .join(RequestDates, Request.request_id == RequestDates.request_id)
            .filter(Request.request_id.in_(all_request_ids))
            .all()
        )

        # Create a response structure
        requests_in_request_id = []
        for req, req_date in results:
            requests_in_request_id.append(
                {
                    "request_id": req.request_id,
                    "staff_id": req.staff_id,
                    "request_submission_date": req.creation_date,
                    "request_date": req_date.request_date.isoformat(),
                    "request_shift": req_date.request_shift,
                    "request_status": req_date.request_status,
                }
            )

        for request_info in requests_in_request_id:
            request_date = datetime.strptime(
                request_info["request_date"], "%Y-%m-%d"
            ).date()
            if week_start <= request_date <= week_end:
                if request_info["request_status"] == "Approved":
                    weekly_arrangement[str(request_date)] = [
                        f'WFH - {request_info["request_shift"]}'
                    ]
                elif request_info["request_status"] == "Pending Withdrawal":
                    weekly_arrangement[str(request_date)] = [
                        f'Home - {request_info["request_shift"]}',
                        "Pending: Office",
                    ]
                elif request_info["request_status"] == "Pending Approval":
                    weekly_arrangement[str(request_date)] = [
                        "Office",
                        f'Pending: WFH - {request_info["request_shift"]}',
                    ]

        return (
            jsonify(
                {
                    "code": 200,
                    "data": weekly_arrangement,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": f"Failed to fetch requests: {str(e)}"}), 500


# Helper function to calculate date range
def get_date_range():
    today = datetime.today()
    start_date = today - timedelta(days=60)
    end_date = today + timedelta(days=90)
    return [
        (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range((end_date - start_date).days + 1)
    ]


# Helper function to initialize department schedule structure
def initialize_dept_schedule(dept, num_employees, all_dates):
    return {
        dept: {
            "num_employee": num_employees,
            **{date: {"AM": [], "PM": [], "Full": []} for date in all_dates},
        }
    }


# Helper function to add employee to department schedule
def add_employee_to_schedule(
    dept_dict, key, request_date_str, request_shift, staff_schedule
):
    if request_date_str in dept_dict[key]:
        dept_dict[key][request_date_str][request_shift].append(staff_schedule)


# Helper function to query and organize schedule data
def fetch_schedule_data(filter_conditions):
    return (
        db.session.query(
            Request.staff_id,
            Employee.staff_fname,
            Employee.staff_lname,
            Employee.dept,
            Employee.position,
            Employee.reporting_manager,
            RequestDates.request_date,
            RequestDates.request_shift,
            RequestDates.request_status,
        )
        .join(Employee, Employee.staff_id == Request.staff_id)
        .join(RequestDates, Request.request_id == RequestDates.request_id)
        .filter(*filter_conditions)
        .all()
    )


# Recursive function to get all team members for a given manager
def get_team_members(staff_id, data, visited=None, staff_details=None):
    if visited is None:
        visited = set()
    if staff_details is None:
        staff_details = {}

    if staff_id in visited:
        return staff_details

    visited.add(staff_id)

    for member in data:
        if member["reporting_manager"] == staff_id:
            staff_details[member["staff_id"]] = {
                "staff_name": member["staff_name"],
                "dept": member["dept"],
                "position": member["position"],
            }
            # Recursive call to find team members under this member
            get_team_members(member["staff_id"], data, visited, staff_details)

    return staff_details


# Endpoint to retrieve organizational schedule
@app.route("/o_get_org_schedule", methods=["GET"])
def o_get_org_schedule():
    try:
        all_dates = get_date_range()
        dept_dict = {}

        # Fetch and initialize department data
        num_employee = (
            db.session.query(
                Employee.dept, func.count(Employee.staff_id).label("staff_count")
            )
            .group_by(Employee.dept)
            .all()
        )
        for dept, staff_count in num_employee:
            dept_dict.update(initialize_dept_schedule(dept, staff_count, all_dates))

        # Query and process schedule data
        results = fetch_schedule_data([])
        for (
            staff_id,
            fname,
            lname,
            dept,
            position,
            manager,
            date,
            shift,
            status,
        ) in results:
            if status == "Approved":
                staff_schedule = {
                    "staff_id": staff_id,
                    "name": f"{fname} {lname}",
                    "position": position,
                    "reporting_manager": manager,
                    "request_status": status,
                }
                add_employee_to_schedule(
                    dept_dict, dept, date.strftime("%Y-%m-%d"), shift, staff_schedule
                )

        return jsonify(dept_dict), 200

    except Exception as e:
        return (
            jsonify(
                {
                    "message": "An error occurred while retrieving the schedule.",
                    "error": str(e),
                }
            ),
            500,
        )


# Endpoint to retrieve manager's team schedule
@app.route("/m_get_team_schedule/<int:staff_id>", methods=["GET"])
def m_get_team_schedule(staff_id):
    try:
        all_dates = get_date_range()
        employee_details = invoke_http(
            employee_URL + f"/get_details/{staff_id}", method="GET"
        )
        employee_dept = employee_details["data"]["dept"]
        position = employee_details["data"]["position"]

        response = invoke_http(employee_URL + "/get_all_employees", method="GET")

        all_team_members = get_team_members(staff_id, response["data"])

        # Edit this code
        if position == "Director":
            subordinate_dict = {}
            # Get the direct subordinates of the director
            direct_subordinates = invoke_http(
                employee_URL + f"/get_staff/{staff_id}", method="GET"
            )

            # For each subordinate under the director
            if direct_subordinates["data"][0]["role"] == 3:
                for subordinate in direct_subordinates["data"]:
                    sub_id = subordinate["staff_id"]
                    sub_dept = subordinate["dept"]
                    sub_name = subordinate["staff_fname"] + subordinate["staff_lname"]
                    sub_position = subordinate["position"]

                    all_team_members = get_team_members(sub_id, response["data"])
                    # Initialize the department schedule structure for this subordinate
                    subordinate_schedule = initialize_dept_schedule(
                        sub_dept, len(all_team_members), get_date_range()
                    )

                    # Fetch schedule data specifically for this subordinate
                    schedule_data = fetch_schedule_data(
                        [
                            Employee.reporting_manager == sub_id,
                            RequestDates.request_status.in_(
                                ["Pending Approval", "Approved"]
                            ),
                        ]
                    )

                    # Populate the subordinate's schedule with dates and shifts
                    for (
                        id,
                        fname,
                        lname,
                        dept,
                        position,
                        manager,
                        date,
                        shift,
                        status,
                    ) in schedule_data:
                        staff_schedule = {
                            "staff_id": id,
                            "name": f"{fname} {lname}",
                            "position": position,
                        }

                        add_employee_to_schedule(
                            subordinate_schedule,
                            dept,
                            date.strftime("%Y-%m-%d"),
                            shift,
                            staff_schedule,
                        )

                    # Add the subordinate's completed schedule to the overall dictionary
                    subordinate_dict[sub_id] = subordinate_schedule[sub_dept]

                return jsonify(subordinate_dict), 200

            else:
                # Initialize team schedule structure with staff_id as the only key
                team_schedule = {
                    staff_id: initialize_dept_schedule(
                        employee_dept, len(all_team_members), all_dates
                    )[employee_dept]
                }

                # Query and process team schedule data
                results = fetch_schedule_data(
                    [RequestDates.request_status.in_(["Pending Approval", "Approved"])]
                )

                # Populate the team schedule structure for each relevant team member
                for (
                    member_id,
                    fname,
                    lname,
                    dept,
                    position,
                    manager,
                    date,
                    shift,
                    status,
                ) in results:
                    if member_id in all_team_members:
                        staff_schedule = {
                            "staff_id": member_id,
                            "name": f"{fname} {lname}",
                            "position": position,
                            "reporting_manager": manager,
                            "request_status": status,
                        }
                        # Add the team member's schedule to the manager's schedule dictionary
                        add_employee_to_schedule(
                            team_schedule,
                            staff_id,
                            date.strftime("%Y-%m-%d"),
                            shift,
                            staff_schedule,
                        )

                # Return the team schedule nested under the manager's ID
                return jsonify(team_schedule), 200

        else:
            # Initialize team schedule
            dept_dict = initialize_dept_schedule(
                employee_dept, len(all_team_members), all_dates
            )

            # Query and process team schedule data
            results = fetch_schedule_data(
                [RequestDates.request_status.in_(["Pending Approval", "Approved"])]
            )
            for (
                staff_id,
                fname,
                lname,
                dept,
                position,
                manager,
                date,
                shift,
                status,
            ) in results:
                if staff_id in all_team_members:
                    staff_schedule = {
                        "staff_id": staff_id,
                        "name": f"{fname} {lname}",
                        "position": position,
                        "reporting_manager": manager,
                        "request_status": status,
                    }
                    add_employee_to_schedule(
                        dept_dict,
                        dept,
                        date.strftime("%Y-%m-%d"),
                        shift,
                        staff_schedule,
                    )

            return jsonify(dept_dict), 200

    except Exception as e:
        return (
            jsonify(
                {
                    "message": "An error occurred while retrieving the schedule.",
                    "error": str(e),
                }
            ),
            500,
        )


# Endpoint to retrieve specific employee's team schedule
@app.route("/s_get_team_schedule/<int:staff_id>", methods=["GET"])
def s_get_team_schedule(staff_id):
    try:
        all_dates = get_date_range()
        employee_details = invoke_http(
            employee_URL + f"/get_details/{staff_id}", method="GET"
        )
        employee_dept = employee_details["data"]["dept"]
        employee_position = employee_details["data"]["position"]
        employee_role = employee_details["data"]["role"]
        employee_reporting_manager = employee_details["data"]["reporting_manager"]

        # Initialize employee-specific schedule
        num_employee = (
            db.session.query(
                Employee.dept, func.count(Employee.staff_id).label("staff_count")
            )
            .filter(
                Employee.dept == employee_dept,
                Employee.position == employee_position,
                Employee.role == employee_role,
                Employee.reporting_manager == employee_reporting_manager,
            )
            .group_by(Employee.dept)
            .first()
        )

        department, staff_count = num_employee
        dept_dict = initialize_dept_schedule(department, staff_count, all_dates)

        # Query and process specific employee's schedule data
        results = fetch_schedule_data(
            [
                RequestDates.request_status.in_(["Pending Approval", "Approved"]),
                Employee.position == employee_position,
                Employee.role == employee_role,
            ]
        )
        for (
            staff_id,
            fname,
            lname,
            dept,
            position,
            manager,
            date,
            shift,
            status,
        ) in results:
            staff_schedule = {
                "staff_id": staff_id,
                "name": f"{fname} {lname}",
                "role": position,
                "reporting_manager": manager,
                "request_status": status,
            }
            add_employee_to_schedule(
                dept_dict, dept, date.strftime("%Y-%m-%d"), shift, staff_schedule
            )

        return jsonify(dept_dict), 200

    except Exception as e:
        return (
            jsonify(
                {
                    "message": "An error occurred while retrieving the schedule.",
                    "error": str(e),
                }
            ),
            500,
        )


# Retrieve wfh count and total by department
@app.route("/get_wfh_status", methods=["GET"])
def get_wfh_status():
    results = (
        db.session.query(Employee.staff_id, RequestDates.request_date)
        .join(Request, Request.request_id == RequestDates.request_id)
        .join(Employee, Employee.staff_id == Request.staff_id)
        .all()
    )
    num_employee_in_dept = db.session.query(
        Employee.staff_id
    ).count()  # Count the number of employees in the department
    status = {}
    for result in results:
        date_str = result[1].isoformat()  # Convert date to string in YYYY-MM-DD format
        staff_id = result[0]  # staff_id
        if date_str not in status:
            status[date_str] = [staff_id]  # Initialize the list with the first staff_id
        elif staff_id not in status[date_str]:
            status[date_str].append(
                staff_id
            )  # Add staff_id to the existing list for this date
    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta

    def get_date_ranges():
        today = datetime.today().date()  # Get today's date as a date object
        # Calculate the start date for 2 months ago
        start_date_past = today - relativedelta(months=2)
        # Calculate the end date for 3 months in the future
        end_date_future = today + relativedelta(months=3)
        # Generate list of past 2 months dates
        date_list = []
        for i in range(60):  # Approximately 60 days in 2 months
            past_date = start_date_past + timedelta(days=i)
            date_list.append(past_date.strftime("%Y-%m-%d"))  # Format to YYYY-MM-DD
        # Generate list of next 3 months dates
        for i in range(90):  # Approximately 90 days in 3 months
            future_date = today + timedelta(days=i)
            if future_date > today:  # Only include future dates
                date_list.append(
                    future_date.strftime("%Y-%m-%d")
                )  # Format to YYYY-MM-DD
        return date_list

    date_list = get_date_ranges()
    for date in date_list:
        if date not in status:
            status[date] = []
    # Return the result as JSON with employee count included
    return jsonify(
        {
            "code": 200,
            "data": status,
            "num_employee_in_dept": num_employee_in_dept,  # Include the count of employees in the response
        }
    )


# Retrieve wfh count and total by department
@app.route("/get_wfh_status_by_team/<int:staff_id>", methods=["GET"])
def get_wfh_status_by_team(staff_id):
    response = invoke_http(employee_URL + "/get_all_employees", method="GET")

    # Recursive function to get all team members for a given manager
    def get_team_members(staff_id, data, visited=None, staff_details=None):
        if visited is None:
            visited = set()
        if staff_details is None:
            staff_details = {}

        if staff_id in visited:
            return staff_details

        visited.add(staff_id)

        for member in data:
            if member["reporting_manager"] == staff_id:
                staff_details[member["staff_id"]] = {
                    "staff_name": member["staff_name"],
                    "dept": member["dept"],
                    "position": member["position"],
                }
                # Recursive call to find team members under this member
                get_team_members(member["staff_id"], data, visited, staff_details)

        return staff_details

    all_team_members = get_team_members(staff_id, response["data"])

    results = (
        db.session.query(Employee.staff_id, RequestDates.request_date)
        .join(Request, Request.request_id == RequestDates.request_id)
        .join(Employee, Employee.staff_id == Request.staff_id)
        .filter(RequestDates.request_status == "Approved")
        .all()
    )

    num_employee_in_dept = len(all_team_members)

    status = {}
    for result in results:
        date_str = result[1].isoformat()  # Convert date to string in YYYY-MM-DD format
        staff_id = result[0]  # staff_id
        if staff_id in all_team_members.keys():
            if date_str not in status:
                status[date_str] = [
                    staff_id
                ]  # Initialize the list with the first staff_id
            elif staff_id not in status[date_str]:
                status[date_str].append(
                    staff_id
                )  # Add staff_id to the existing list for this date

    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta

    def get_date_ranges():
        today = datetime.today().date()  # Get today's date as a date object
        # Calculate the start date for 2 months ago
        start_date_past = today - relativedelta(months=2)
        # Calculate the end date for 3 months in the future
        end_date_future = today + relativedelta(months=3)
        # Generate list of past 2 months dates
        date_list = []
        for i in range(60):  # Approximately 60 days in 2 months
            past_date = start_date_past + timedelta(days=i)
            date_list.append(past_date.strftime("%Y-%m-%d"))  # Format to YYYY-MM-DD
        # Generate list of next 3 months dates
        for i in range(90):  # Approximately 90 days in 3 months
            future_date = today + timedelta(days=i)
            if future_date > today:  # Only include future dates
                date_list.append(
                    future_date.strftime("%Y-%m-%d")
                )  # Format to YYYY-MM-DD
        return date_list

    date_list = get_date_ranges()
    for date in date_list:
        if date not in status:
            status[date] = []
    # Return the result as JSON with employee count included
    return jsonify(
        {
            "code": 200,
            "data": status,
            "num_employee_in_dept": num_employee_in_dept,  # Include the count of employees in the response
        }
    )


# if __name__ == "__main__":
#     app.run()
