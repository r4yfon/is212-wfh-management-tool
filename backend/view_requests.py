from flask import Flask, jsonify
from flask_cors import CORS
from os import environ
from database import db

app = Flask(__name__)
app.config.from_object("config.Config")
db.init_app(app)
CORS(app, resources={r"/*": {"origins": "*"}})

from database import Employee, Request, RequestDates

employee_URL = environ.get("EMPLOYEE_URL") or "http://localhost:5000/employee"
request_URL = environ.get("REQUEST_URL") or "http://localhost:5001/request"
request_dates_URL = (
    environ.get("REQUEST_DATES_URL") or "http://localhost:5002/request_dates"
)


# Staff view own requests
@app.route("/view_requests/s_retrieve_requests/<int:s_staff_id>", methods=["GET"])
def s_retrieve_requests(s_staff_id):
    """
    Parameters:
    staff_id (int): The staff_id

    Success response:
    [
        {
            "request_id": 1,
            "staff_id": 150488,
            "creation_date": "2024-05-28",
            "apply_reason": "Family event",
            "reject_reason": None,
            "wfh_dates": [
                {
                    "request_date_id": 1,
                    "request_date": "2024-09-22",
                    "request_shift": "Full",
                    "request_status": "Pending Approval",
                    "rescind_reason": None,
                    "withdraw_reason": None
                }
            ]
        },
        {
            "request_id": 2,
            "staff_id": 150446,
            "creation_date": "2024-09-10",
            "apply_reason": "Medical appointment",
            "reject_reason": None,
            "wfh_dates": [
                {
                    "request_date_id": 3,
                    "request_date": "2024-09-10",
                    "request_shift": "Full",
                    "request_status": "Pending Approval",
                    "rescind_reason": None,
                    "withdraw_reason": None
                }
            ]
        }
    ]
    """
    try:
        # Get all requests for this staff
        requests = Request.query.filter_by(staff_id=s_staff_id).all()

        # Format response
        requests_list = []
        for req in requests:
            request_dates = RequestDates.query.filter_by(
                request_id=req.request_id
            ).all()

            wfh_dates = []
            for date in request_dates:
                wfh_dates.append(
                    {
                        "request_date_id": date.request_date_id,
                        "request_date": str(date.request_date),
                        "request_shift": date.request_shift,
                        "request_status": date.request_status,
                        "rescind_reason": date.rescind_reason,
                        "withdraw_reason": date.withdraw_reason,
                    }
                )

            requests_list.append(
                {
                    "request_id": req.request_id,
                    "staff_id": req.staff_id,
                    "creation_date": str(req.creation_date),
                    "apply_reason": req.apply_reason,
                    "reject_reason": req.reject_reason,
                    "wfh_dates": wfh_dates,
                }
            )

        response = jsonify(requests_list)
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/view_requests/m_retrieve_requests/<int:m_staff_id>", methods=["GET"])
def m_retrieve_requests(m_staff_id):
    """
    Success response:
    [
        {
            "request_id": 1,
            "staff_id": 150488,
            "staff_name": "Jacob Tan",
            "creation_date": "2024-05-28",
            "apply_reason": "Family event",
            "reject_reason": None,
            "wfh_dates": [
                {
                    "request_date_id": 1,
                    "request_date": "2024-09-22",
                    "request_shift": "Full",
                    "request_status": "Pending Approval",
                    "rescind_reason": None,
                    "withdraw_reason": None
                }
            ]
        },
        {
            "request_id": 2,
            "staff_id": 150446,
            "staff_name": "Daniel Tan",
            "creation_date": "2024-09-10",
            "apply_reason": "Medical appointment",
            "reject_reason": None,
            "wfh_dates": [
                {
                    "request_date_id": 3,
                    "request_date": "2024-09-10",
                    "request_shift": "Full",
                    "request_status": "Pending Approval",
                    "rescind_reason": None,
                    "withdraw_reason": None
                }
            ]
        }
    ]
    """
    try:
        # Query Employee, Request, and RequestDates
        results = (
            db.session.query(
                Employee.staff_id,
                Employee.staff_fname,
                Employee.staff_lname,
                Request.request_id,
                Request.creation_date,
                Request.apply_reason,
                Request.reject_reason,
                RequestDates.request_date_id,
                RequestDates.request_date,
                RequestDates.request_shift,
                RequestDates.request_status,
                RequestDates.rescind_reason,
                RequestDates.withdraw_reason,
            )
            .join(Request, Employee.staff_id == Request.staff_id)
            .join(RequestDates, Request.request_id == RequestDates.request_id)
            .filter(Employee.reporting_manager == m_staff_id)
            .all()
        )

        # Organizing the results
        request_dict_map = {}
        request_list = []

        for row in results:
            staff_id = row[0]
            staff_fname = row[1]
            staff_lname = row[2]
            request_id = row[3]
            creation_date = row[4].isoformat()
            apply_reason = row[5]
            reject_reason = row[6]
            request_date_id = row[7]
            request_date = row[8].isoformat()
            request_shift = row[9]
            request_status = row[10]
            rescind_reason = row[11]
            withdraw_reason = row[12]

            if request_id not in request_dict_map:
                request_dict = {
                    "request_id": request_id,
                    "staff_id": staff_id,
                    "staff_name": f"{staff_fname} {staff_lname}",
                    "creation_date": creation_date,
                    "apply_reason": apply_reason,
                    "reject_reason": reject_reason,
                    "wfh_dates": [],
                }
                request_dict_map[request_id] = request_dict
                request_list.append(request_dict)
            else:
                request_dict = request_dict_map[request_id]

            # Collect request date information
            request_date_dict = {
                "request_date_id": request_date_id,
                "request_date": request_date,
                "request_shift": request_shift,
                "request_status": request_status,
                "rescind_reason": rescind_reason,
                "withdraw_reason": withdraw_reason,
            }

            # Append the date to the list of dates for this request
            request_dict["wfh_dates"].append(request_date_dict)

        # Return the data in JSON format
        return jsonify({"code": 200, "data": request_list}), 200

    except Exception as e:
        return (
            jsonify(
                {
                    "code": 500,
                    "error": f"An error occurred while retrieving requests for manager staff_id {m_staff_id}: {e}",
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(port=5101, debug=True)
