from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get(
    'dbURL') or 'mysql+mysqlconnector://root:root@localhost:3306/wfh_scheduling'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)
CORS(app, resources={r"/*": {"origins": "*"}})

# employee_URL = environ.get('employee_URL') or "http://localhost:5000/employee"
request_URL = environ.get('request_URL') or "http://localhost:5001/"
request_dates_URL = environ.get(
    'request_dates_URL') or "http://localhost:5002/"


def get_week_from_date(date_entered):
    """
    Get the start and end dates of the week based on the date_entered. By default, week starts on Monday and ends on Sunday, so we change it to be from Sunday to Monday.
    ---
    Parameters:
        date_entered (string): The date in the format YYYY-MM-DD

    Returns:
        tuple(
            start_date (date): The start date of the week
            end_date (date): The end date of the week
        )
    """

    date_entered = datetime.strptime(date_entered, '%Y-%m-%d').date()
    # Check if date entered falls on a Sunday
    if date_entered.weekday() == 6:
        # If it does, set it to be the start date
        start_date = date_entered
    else:
        # If it doesn't, set it to be the previous Sunday
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
            Weekly schedule for the given staff. The week is calculated based on the date_entered.
            It will be in a dictionary, where the keys are the dates and the values are the location and shift (if applicable).

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

    # Query the requests submitted by the staff_id
    try:
        # This will get all the WFH requests made by the staff_id
        all_requests = requests.get(
            f'{request_URL}/get_all_requests/{int(staff_id)}').json()['data']

        weekly_arrangement = {}
        request_id_list = []

        # Store all the request_ids for the given staff_id into request_id_list
        for request in all_requests:
            request_id = request['request_id']
            request_id_list.append(request_id)

        # Save all the re quest_ids in a list to get all request dates: make the function more efficient
        requests_in_request_id = requests.post(
            f'{request_dates_URL}/get_request_dates_by_request_ids',
            json={'request_ids': request_id_list}).json()['data']

        for request_info in requests_in_request_id:
            request_date = datetime.strptime(
                request_info['request_date'], '%Y-%m-%d').date()
            if week_start <= request_date <= week_end and request_info['request_status'] == 'Approved':
                weekly_arrangement[str(
                    request_date)] = f'Home - {request_info["request_shift"]}'

        for date in (week_start + timedelta(n) for n in range((week_end - week_start).days + 1)):
            if str(date) not in weekly_arrangement:
                weekly_arrangement[str(date)] = "Office"

        return jsonify({
            "code": 200,
            "data": weekly_arrangement,
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to fetch requests: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)
