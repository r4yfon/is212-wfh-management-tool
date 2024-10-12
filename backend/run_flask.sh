#!/bin/bash

# Set the directory where the files are located
FLASK_DIR=$(pwd)

# make this shit executable: chmod +x run_flask.sh

# Start the Flask applications in separate terminal windows
wt -w myWindow nt -p "Terminal" -d "$FLASK_DIR" --title "employee.py" -- bash -c "export FLASK_APP=employee.py && export FLASK_ENV=development && export FLASK_DEBUG=1 && flask run --port 5000"

wt -w myWindow nt -p "Terminal" -d "$FLASK_DIR" --title "request.py" -- bash -c "export FLASK_APP=request.py && export FLASK_ENV=development && export FLASK_DEBUG=1 && flask run --port 5001"

wt -w myWindow nt -p "Terminal" -d "$FLASK_DIR" --title "request_dates.py" -- bash -c "export FLASK_APP=request_dates.py && export FLASK_ENV=development && export FLASK_DEBUG=1 && flask run --port 5002"

wt -w myWindow nt -p "Terminal" -d "$FLASK_DIR" --title "view_schedule.py" -- bash -c "export FLASK_APP=view_schedule.py && export FLASK_ENV=development && export FLASK_DEBUG=1 && flask run --port 5100"

wt -w myWindow nt -p "Terminal" -d "$FLASK_DIR" --title "view_requests.py" -- bash -c "export FLASK_APP=view_requests.py && export FLASK_ENV=development && export FLASK_DEBUG=1 && flask run --port 5101"

wt -w myWindow nt -p "Terminal" -d "$FLASK_DIR" --title "reject_requests.py" -- bash -c "export FLASK_APP=view_requests.py && export FLASK_ENV=development && export FLASK_DEBUG=1 && flask run --port 5102"

wt -w myWindow nt -p "Terminal" -d "$FLASK_DIR" --title "status_log.py" -- bash -c "export FLASK_APP=view_requests.py && export FLASK_ENV=development && export FLASK_DEBUG=1 && flask run --port 5003"
