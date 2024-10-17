from flask import Flask, request, jsonify
import requests
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime, timedelta
from request import Request
from employee import Employee
from request_dates import RequestDates
from input_validation import check_date_valid
from flask_cors import CORS
from invokes import invoke_http

app = Flask(__name__)
app.config.from_object("config.Config")
db = SQLAlchemy(app)
CORS(app, resources={r"/*": {"origins": "*"}})

employee_URL = environ.get("employee_URL") or "http://localhost:5000/employee"
request_URL = environ.get("request_URL") or "http://localhost:5001/request"
request_dates_URL = (
    environ.get("request_dates_URL") or "http://localhost:5002/request_dates"
)


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



@app.route("/o_get_org_schedule", methods=["GET"])
def o_get_org_schedule():
    try:
        # Perform a union join query to get all relevant data
        results = db.session.query(
            Request.staff_id,
            Employee.staff_fname,
            Employee.staff_lname,
            Employee.dept,
            RequestDates.request_date,
            RequestDates.request_shift,
            RequestDates.request_status
        ).join(Employee, Employee.staff_id == Request.staff_id) \
        .join(RequestDates, Request.request_id == RequestDates.request_id) \
        .filter(RequestDates.request_status.in_(["Pending Approval", "Approved"])) \
        .all()

        dept_dict = {}  # Dictionary to store results by department

        for staff_id, staff_fname, staff_lname, dept, request_date, request_shift, request_status in results:
            request_date_str = request_date.strftime("%Y-%m-%d")

            if dept not in dept_dict:
                dept_dict[dept] = {}
            if request_date_str not in dept_dict[dept]:
                dept_dict[dept][request_date_str] = []

            staff_schedule = {
                "staff_name": f"{staff_fname} {staff_lname}",
                "staff_id": staff_id,
                "schedule": []
            }

            if request_status == "Pending Approval":
                staff_schedule["schedule"].append(f"Pending - {request_shift}")
            else:
                staff_schedule["schedule"].append(f"WFH - {request_shift}")

            existing_staff = next(
                (staff for staff in dept_dict[dept][request_date_str] if staff["staff_id"] == staff_id),
                None
            )

            if existing_staff:
                existing_staff["schedule"].append(staff_schedule["schedule"][0])
            else:
                dept_dict[dept][request_date_str].append(staff_schedule)

        return jsonify(dept_dict), 200  # Return 200 OK with the schedule

    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving the schedule.", "error": str(e)}), 500




@app.route("/m_get_team_schedule/<int:staff_id>", methods=["GET"])
def m_get_team_schedule(staff_id):
    try:
        response = invoke_http(employee_URL + "/get_all_employees", method="GET")

        def get_team_members(staff_id, visited=None, staff_details=None):
            if visited is None:
                visited = set()
            if staff_details is None:
                staff_details = {}

            if staff_id in visited:
                return staff_details

            visited.add(staff_id)

            for member in response["data"]:
                if member["reporting_manager"] == staff_id:
                    staff_details[member["staff_id"]] = {
                        "staff_name": member["staff_name"],
                        "dept": member["dept"],
                        "position": member["position"],
                    }

                    staff_details.update(get_team_members(member["staff_id"], visited, staff_details))

            return staff_details

        all_team_members = get_team_members(staff_id)

        results = db.session.query(
            Request.staff_id,
            Employee.staff_fname,
            Employee.staff_lname,
            Employee.dept,
            RequestDates.request_date,
            RequestDates.request_shift,
            RequestDates.request_status
        ).join(Employee, Employee.staff_id == Request.staff_id) \
        .join(RequestDates, Request.request_id == RequestDates.request_id) \
        .filter(RequestDates.request_status.in_(["Pending Approval", "Approved"])) \
        .all()

        dept_dict = {}

        for staff_id, staff_fname, staff_lname, dept, request_date, request_shift, request_status in results:
            if staff_id in all_team_members:
                request_date_str = request_date.strftime("%Y-%m-%d")

                if dept not in dept_dict:
                    dept_dict[dept] = {}
                if request_date_str not in dept_dict[dept]:
                    dept_dict[dept][request_date_str] = []

                staff_schedule = {
                    "staff_name": f"{staff_fname} {staff_lname}",
                    "staff_id": staff_id,
                    "schedule": []
                }

                if request_status == "Pending Approval":
                    staff_schedule["schedule"].append(f"Pending - {request_shift}")
                else:
                    staff_schedule["schedule"].append(f"WFH - {request_shift}")

                existing_staff = next(
                    (staff for staff in dept_dict[dept][request_date_str] if staff["staff_id"] == staff_id),
                    None
                )

                if existing_staff:
                    existing_staff["schedule"].append(staff_schedule["schedule"][0])
                else:
                    dept_dict[dept][request_date_str].append(staff_schedule)

        return jsonify(dept_dict), 200

    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving the team schedule.", "error": str(e)}), 500



@app.route("/s_get_team_schedule/<int:staff_id>", methods=["GET"])
def s_get_team_schedule(staff_id):
    try:
        results = db.session.query(
            Request.staff_id,
            Employee.staff_fname,
            Employee.staff_lname,
            Employee.dept,
            RequestDates.request_date,
            RequestDates.request_shift,
            RequestDates.request_status
        ).join(Employee, Employee.staff_id == Request.staff_id) \
        .join(RequestDates, Request.request_id == RequestDates.request_id) \
        .filter(RequestDates.request_status.in_(["Pending Approval", "Approved"]),
                Employee.position == "Senior Engineers",
                Employee.role == 2) \
        .all()

        dept_dict = {}

        for staff_id, staff_fname, staff_lname, dept, request_date, request_shift, request_status in results:
            request_date_str = request_date.strftime("%Y-%m-%d")

            if dept not in dept_dict:
                dept_dict[dept] = {}
            if request_date_str not in dept_dict[dept]:
                dept_dict[dept][request_date_str] = []

            staff_schedule = {
                "staff_name": f"{staff_fname} {staff_lname}",
                "staff_id": staff_id,
                "schedule": []
            }

            if request_status == "Pending Approval":
                staff_schedule["schedule"].append(f"Pending - {request_shift}")
            else:
                staff_schedule["schedule"].append(f"WFH - {request_shift}")

            existing_staff = next(
                (staff for staff in dept_dict[dept][request_date_str] if staff["staff_id"] == staff_id),
                None
            )

            if existing_staff:
                existing_staff["schedule"].append(staff_schedule["schedule"][0])
            else:
                dept_dict[dept][request_date_str].append(staff_schedule)

        return jsonify(dept_dict), 200

    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving the staff schedule.", "error": str(e)}), 500




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
@app.route("/get_wfh_status/<string:department>", methods=["GET"])
def get_wfh_status_by_dept(department):
    results = (
        db.session.query(Employee.staff_id, RequestDates.request_date)
        .join(Request, Request.request_id == RequestDates.request_id)
        .join(Employee, Employee.staff_id == Request.staff_id)
        .filter(Employee.dept == department)
        .all()
    )

    num_employee_in_dept = (
        db.session.query(Employee.staff_id).filter(Employee.dept == department).count()
    )  # Count the number of employees in the department

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5100, debug=True)
