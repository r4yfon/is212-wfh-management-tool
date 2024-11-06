from flask import Flask, request, jsonify
from database import db, StatusLog
from flask_cors import CORS
from datetime import datetime


app = Flask(__name__)
app.config.from_object("config.Config")
CORS(app, resources={r"/*": {"origins": "*"}})


# Add event to the log
@app.route("/status_log/add_event", methods=["POST"])
def add_event():
    """
    Log a new status change event.
    ---
    Request body:
    {
        "request_id": <request_id>,
        "action": "<action>",
        "reason": "<reason>"
    }
    Success response:
    {
        "code": 201,
        "message": "Event logged successfully",
        "data": { ... }
    }
    """
    data = request.get_json()

    # Validate input data
    if not data or "request_id" not in data or "action" not in data:
        return (
            jsonify(
                {
                    "code": 400,
                    "error": "Invalid input. 'request_id' and 'action' are required.",
                }
            ),
            400,
        )

    request_id = data["request_id"]
    action = data["action"]
    reason = data.get("reason")

    try:
        # Create a new StatusLog entry
        status_log = StatusLog(request_id=request_id, action=action, reason=reason)
        db.session.add(status_log)
        db.session.commit()

        return (
            jsonify(
                {
                    "code": 201,
                    "message": "Event logged successfully",
                    "data": status_log.json(),  # Return the logged status
                }
            ),
            201,
        )

    except Exception as e:
        print("Error:", str(e))  # Debugging log
        return (
            jsonify(
                {"code": 500, "error": "An error occurred while logging the event."}
            ),
            500,
        )


if __name__ == "__main__":
    app.run(port=5003, debug=True)
