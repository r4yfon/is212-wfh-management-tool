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
    'request_dates_URL') or "http://localhost:5002/request_dates"


@app.route("/view_weekly_schedule/<int:staff_id>/<string:date_entered>")
def view_weekly_schedule(staff_id, date_entered):
    """
    View weekly schedule based on date entered
    ---
    responses:
        200:
            description: Return weekly schedule
        404:
            description: Unable to find weekly schedule
    """
    # Get the start and end dates of the week based on the date_entered
    date_entered = datetime.strptime(date_entered, '%Y-%m-%d').date()
    start_date = date_entered - timedelta(days=date_entered.weekday())
    end_date = start_date + timedelta(days=6)

    # Query the requests submitted by the staff_id
    try:
        all_requests = requests.get(
            f'{request_URL}/get_all_requests/{int(staff_id)}').json()['data']
        
        return jsonify(all_requests)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch requests: {str(e)}"}), 500

    # Get the request dates for the week
    # request_dates = []
    # for request in requests:
    #     dates = RequestDates.query.filter(
    #         RequestDates.request_id == request.id,
    #         RequestDates.date >= start_date,
    #         RequestDates.date <= end_date
    #     ).all()
    #     request_dates.extend(dates)

    # # Process the request dates and return the response
    # if request_dates:
    #     return jsonify({
    #         "code": 200,
    #         "data": [date.json() for date in request_dates]
    #     })
    # else:
    #     return jsonify({
    #         "code": 404,
    #         "error": "No request dates found for the specified week"
    #     }), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011, debug=True)
