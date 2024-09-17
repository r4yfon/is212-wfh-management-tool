from flask import Flask, request, jsonify
import requests
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime, timedelta
from request import Request
from request_dates import RequestDates

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)

request_URL = environ.get('request_URL') or "http://localhost:5001/"


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


@app.route("/view_weekly_schedule/<int:staff_id>/<string:date_entered>")
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
                "2023-10-01": "Home - PM",
                "2023-10-02": "Office",
                "2023-10-03": "Office",
                "2023-10-04": "Office",
                "2023-10-05": "Office",
                "2023-10-06": "Office",
                "2023-10-07": "Office",
            }
    """

    week_start, week_end = get_week_from_date(date_entered)
    weekly_arrangement = {}
    for n in range((week_end - week_start).days + 1):
        weekly_arrangement[str(week_start + timedelta(days=n))] = "Office"

    # Query the requests submitted by the staff_id
    try:
        # This will get all the WFH requests made by the staff_id
        all_request_ids = requests.get(
            f'{request_URL}/get_request_ids/{int(staff_id)}').json()['data']

        """
        Get requests based on the provided request_ids. The request_ids are all from the same staff_id.
        ---
        Parameters (in request body):
            request_ids (list): A list of request IDs. [1, 2, 3]

        Successful response:
            {
                "code": 200,
                "data": [
                    {
                        "manager_approval_date": "2024-09-16",
                        "request_date": "2024-09-15",
                        "request_id": 1,
                        "request_overall_status": "Approved",
                        "request_shift": "PM",
                        "request_status": "Approved",
                        "request_submission_date": "Sun, 15 Sep 2024 00:00:00 GMT",
                        "staff_id": 150488
                    },
                    ...
                ]
            }
        """
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
                "request_overall_status": req.request_status,
                "manager_approval_date": req.manager_approval_date.isoformat() if req.manager_approval_date else None,
                "request_date": req_date.request_date.isoformat(),
                "request_shift": req_date.request_shift,
                "request_status": req_date.request_status
            })

        for request_info in requests_in_request_id:
            request_date = datetime.strptime(
                request_info['request_date'], '%Y-%m-%d').date()
            if week_start <= request_date <= week_end and request_info['request_status'] == 'Approved':
                weekly_arrangement[str(
                    request_date)] = f'Home - {request_info["request_shift"]}'

        return jsonify({
            "code": 200,
            "data": weekly_arrangement,
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to fetch requests: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)
