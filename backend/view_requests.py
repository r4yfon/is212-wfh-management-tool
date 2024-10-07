from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from invokes import invoke_http
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
CORS(app)
#######################################################


# Staff view own requests
@app.route("/s_retrieve_requests", methods=['GET'])
def s_retrieve_requests():
    s_staff_id = "150488"
    # Get all requests made by the staff_id
    response = invoke_http("http://localhost:5001/request/get_requests_by_staff_id/" + s_staff_id, method='GET')

    # Ensure the response contains a 'data' field before processing
    if "data" in response and isinstance(response["data"], list):
        for request in response["data"]:
            request_id = request["request_id"]
            
            # Construct the URL using the request_id
            url = f"http://localhost:5002/request_dates/get_by_request_id/{request_id}"
            
            # Make the invoke_http call to get request dates
            request_dates_response = invoke_http(url, method='GET')
            
            # Add the request_dates_response to the request as a new field
            request["wfh_dates"] = request_dates_response
    
    # Return the modified response including the request_dates
    return jsonify(response)


# manager view requests from requestors
@app.route("/m_retrieve_requests", methods=['GET'])
def m_retrieve_requests():
    m_staff_id = "150555"
    """
    Success response:
    [
        {
            "reason": "Family event",
            "request_dates": [
                "2024-05-29"
            ],
            "request_id": 1,
            "request_status": "Pending Approval",
            "staff_id": 150488,
            "staff_name": "Jacob Tan"
        },
        {
            "reason": "Medical appointment",
            "request_dates": [
                "2024-09-12"
            ],
            "request_id": 2,
            "request_status": "Pending Withdrawal",
            "staff_id": 150488,
            "staff_name": "Jacob Tan"
        }
    ]
    """
    try:
        response = invoke_http("http://localhost:5000/employee/get_staff/" + m_staff_id, method='GET')

        staff_list = []
        staff_name_dict = {}
        for staff in response["data"]:
            staff_list.append((staff["staff_id"]))
            staff_name_dict[staff["staff_id"]] = staff["staff_fname"] + " " + staff["staff_lname"]

        staff_requests = invoke_http("http://localhost:5001/request/get_all_requests", method='GET')

        request_list = []
        for request in staff_requests["data"]:
            if request["staff_id"] in staff_list:
                request_dict = {"staff_id": request["staff_id"], "staff_name": staff_name_dict[request["staff_id"]], "request_id": request["request_id"], "request_dates": [], "reason": request["apply_reason"]}
                
                staff_request_dates = invoke_http("http://localhost:5002/request_dates/get_by_request_id/" + str(request["request_id"]), method='GET')
                for request_dates in staff_request_dates[0]["data"]:
                    if request_dates["request_status"] == "Pending Approval" or request_dates["request_status"] == "Pending Withdrawal":
                        request_dict["request_dates"].append({request_dates["request_date"]: request_dates["request_shift"]})
                        request_dict["request_status"] = request_dates["request_status"]
                if len(request_dict["request_dates"]) > 0:
                    request_list.append(request_dict)

        # Return the modified response including the request_dates
        return jsonify({"code": 200, "data": request_list}), 200

    except Exception as e:
        return jsonify({
                "code": 500,
                "error": f"An error occurred while getting employee requests for manager staff_id {m_staff_id}: {e}"
            }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5101, debug=True)