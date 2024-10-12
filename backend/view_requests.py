from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from invokes import invoke_http
from flask_cors import CORS
from os import environ
from employee import db, Employee
from request import db, Request
from request_dates import db, RequestDates

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
CORS(app)

employee_URL = environ.get(
    'employee_URL') or "http://localhost:5000/employee"
request_URL = environ.get(
    'request_URL') or "http://localhost:5001/request"
request_dates_URL = environ.get(
    'request_dates_URL') or "http://localhost:5002/request_dates"


# # Staff view own requests
# @app.route("/s_retrieve_requests/<int:s_staff_id>", methods=['GET'])
# def s_retrieve_requests(s_staff_id):
#     # Get all requests made by the staff_id
#     response = invoke_http("http://localhost:5001/request/get_requests_by_staff_id/" + str(s_staff_id), method='GET')

#     # Ensure the response contains a 'data' field before processing
#     if "data" in response and isinstance(response["data"], list):
#         for request in response["data"]:
#             request_id = request["request_id"]
            
#             # Construct the URL using the request_id
#             url = f"{request_dates_URL}/get_by_request_id/{request_id}"
            
#             # Make the invoke_http call to get request dates
#             request_dates_response = invoke_http(url, method='GET')
            
#             # Add the request_dates_response to the request as a new field
#             request["wfh_dates"] = request_dates_response
    
#     # Return the modified response including the request_dates
#     return jsonify(response)


# Staff view own requests
@app.route("/s_retrieve_requests/<int:s_staff_id>", methods=['GET'])
def s_retrieve_requests(s_staff_id):
    try:
        # Perform an inner join between Request and RequestDates tables where staff_id matches
        results = db.session.query(Request, RequestDates).join(RequestDates, Request.request_id == RequestDates.request_id).filter(Request.staff_id == s_staff_id).all()

        # Prepare response data
        request_list = []
        request_dict_map = {}

        for request, request_date in results:
            if request.request_id not in request_dict_map:
                request_dict = {
                    "request_id": request.request_id,
                    "staff_id": request.staff_id,
                    "creation_date": request.creation_date.isoformat(),
                    "apply_reason": request.apply_reason,
                    "reject_reason": request.reject_reason,
                    "wfh_dates": []
                }
                request_dict_map[request.request_id] = request_dict
                request_list.append(request_dict)
            else:
                request_dict = request_dict_map[request.request_id]

            # Collect request date information
            request_date_dict = {
                "request_date_id": request_date.request_date_id,
                "request_date": request_date.request_date.isoformat(),
                "request_shift": request_date.request_shift,
                "request_status": request_date.request_status,
                "rescind_reason": request_date.rescind_reason,
                "withdraw_reason": request_date.withdraw_reason
            }

            # Append the date to the list of dates for this request
            request_dict["wfh_dates"].append(request_date_dict)

        # Return the data in JSON format
        return jsonify({
            "code": 200,
            "data": request_list
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "error": f"An error occurred while retrieving requests for staff_id {s_staff_id}: {e}"
        }), 500




# manager view requests from requestors
# @app.route("/m_retrieve_requests/<int:m_staff_id>", methods=['GET'])
# def m_retrieve_requests(m_staff_id):
#     """
#     Success response:
#     [
#         {
#             "reason": "Family event",
#             "request_dates": [
#                 "2024-05-29"
#             ],
#             "request_id": 1,
#             "request_status": "Pending Approval",
#             "staff_id": 150488,
#             "staff_name": "Jacob Tan"
#         },
#         {
#             "reason": "Medical appointment",
#             "request_dates": [
#                 "2024-09-12"
#             ],
#             "request_id": 2,
#             "request_status": "Pending Withdrawal",
#             "staff_id": 150488,
#             "staff_name": "Jacob Tan"
#         }
#     ]
#     """
#     try:
#         response = invoke_http("http://localhost:5000/employee/get_staff/" + str(m_staff_id), method='GET')

#         staff_list = []
#         staff_name_dict = {}
#         for staff in response["data"]:
#             staff_list.append((staff["staff_id"]))
#             staff_name_dict[staff["staff_id"]] = staff["staff_fname"] + " " + staff["staff_lname"]

#         staff_requests = invoke_http("http://localhost:5001/request/get_all_requests", method='GET')

#         request_list = []
#         for request in staff_requests["data"]:
#             if request["staff_id"] in staff_list:
#                 request_dict = {"staff_id": request["staff_id"], "staff_name": staff_name_dict[request["staff_id"]], "request_id": request["request_id"], "request_dates": [], "reason": request["apply_reason"]}
                
#                 staff_request_dates = invoke_http("http://localhost:5002/request_dates/get_by_request_id/" + str(request["request_id"]), method='GET')
#                 for request_dates in staff_request_dates[0]["data"]:
#                     if request_dates["request_status"] == "Pending Approval" or request_dates["request_status"] == "Pending Withdrawal":
#                         request_dict["request_dates"].append({request_dates["request_date"]: request_dates["request_shift"]})
#                         request_dict["request_status"] = request_dates["request_status"]
#                 if len(request_dict["request_dates"]) > 0:
#                     request_list.append(request_dict)

#         # Return the modified response including the request_dates
#         return jsonify({"code": 200, "data": request_list}), 200

#     except Exception as e:
#         return jsonify({
#                 "code": 500,
#                 "error": f"An error occurred while getting employee requests for manager staff_id {m_staff_id}: {e}"
#             }), 500



@app.route("/m_retrieve_requests/<int:m_staff_id>", methods=['GET']) 
def m_retrieve_requests(m_staff_id):
    """
    Success response:
    [
        {
            "reason": "Family event",
            "request_dates": [
                {
                    "2024-09-22": "Full"
                },
                {
                    "2024-05-29": "AM"
                }
            ],
            "request_id": 1,
            "request_status": "Pending Approval",
            "staff_id": 150488,
            "staff_name": "Jacob Tan"
        },
        {
            "reason": "Medical appointment",
            "request_dates": [
                {
                    "2024-09-10": "Full"
                },
                {
                    "2024-09-17": "Full"
                },
                {
                    "2024-09-12": "AM"
                }
            ],
            "request_id": 2,
            "request_status": "Pending Approval",
            "staff_id": 150446,
            "staff_name": "Daniel Tan"
        }
    ]
    """
    try:
        # Join Employee, Request, and RequestDates
        results = db.session.query(
            Employee.staff_id,
            Employee.staff_fname,
            Employee.staff_lname,
            Request.request_id,
            Request.apply_reason,
            RequestDates.request_date,
            RequestDates.request_shift,
            RequestDates.request_status
        ).join(Request, Employee.staff_id == Request.staff_id) \
         .join(RequestDates, Request.request_id == RequestDates.request_id) \
         .filter(Employee.reporting_manager == m_staff_id, 
                 RequestDates.request_status.in_(["Pending Approval", "Pending Withdrawal"])) \
         .all()
        
        print("DAWDAW", results)
        # Organizing the results
        request_dicts = {}
        for row in results:
            print(row)
            staff_id = row[0]
            staff_fname = row[1]
            staff_lname = row[2]
            request_id = row[3]
            apply_reason = row[4]
            request_date = row[5]
            request_shift = row[6]
            request_status = row[7]

            # Convert request_date to string
            request_date_str = request_date.isoformat()  # or use str(request_date) if the format is acceptable

            if request_id not in request_dicts:
                request_dicts[request_id] = {
                    "request_id": request_id,
                    "staff_id": staff_id,
                    "staff_name": f"{staff_fname} {staff_lname}",
                    "reason": apply_reason,
                    "request_status": request_status,
                    "request_dates": []
                }
            request_dicts[request_id]["request_dates"].append({
                request_date_str: request_shift
            })

        # Convert dictionary to list for the response
        request_list = list(request_dicts.values())



        # Return the modified response including the request_dates
        return jsonify({"code": 200, "data": request_list}), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "error": f"An error occurred while getting employee requests for manager staff_id {m_staff_id}: {e}"
        }), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5101, debug=True)