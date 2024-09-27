from flask import Flask, request, jsonify
import requests
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime, timedelta
from request import Request
from request_dates import RequestDates
from input_validation import check_date_valid
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
CORS(app, resources={r"/view_schedule/weekly/*": {"origins": "*"}})

request_URL = environ.get('request_URL') or "http://localhost:5001/request"


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
                "request_submission_date": req.request_date,
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)
