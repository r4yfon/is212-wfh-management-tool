from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from invokes import invoke_http

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)

#######################################################
staff_id = "150488"

@app.route("/retrieve_requests", methods=['GET'])
def retrieve_requests():
    # Get all requests made by the staff_id
    response = invoke_http("http://localhost:5001/request/get_all_requests/" + staff_id, method='GET')

    # Ensure the response contains a 'data' field before processing
    if "data" in response and isinstance(response["data"], list):
        for request in response["data"]:
            request_id = request["request_id"]
            
            # Construct the URL using the request_id
            url = f"http://localhost:5002/request_dates/get_by_request_id/{request_id}"
            
            # Make the invoke_http call to get request dates
            request_dates_response = invoke_http(url, method='GET')
            
            # Add the request_dates_response to the request as a new field
            request["request_dates"] = request_dates_response["data"] if "data" in request_dates_response else []
    
    # Return the modified response including the request_dates
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5110, debug=True)