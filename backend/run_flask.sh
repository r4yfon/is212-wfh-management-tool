#!/bin/bash

# Set the directory where the files are located
FLASK_DIR=$(pwd)

# make this shit executable: chmod +x run_flask.sh

# Start the Flask applications in separate terminal windows
open -a Terminal.app -n --args bash -c "export FLASK_APP=employee.py && export FLASK_ENV=development && export FLASK_DEBUG=1 && flask run --port 5000"

open -a Terminal.app -n --args bash -c "export FLASK_APP=request.py && export FLASK_ENV=development && export FLASK_DEBUG=1 && flask run --port 5001"

open -a Terminal.app -n --args bash -c "export FLASK_APP=request_dates.py && export FLASK_ENV=development && export FLASK_DEBUG=1 && flask run --port 5002"

open -a Terminal.app -n --args bash -c "export FLASK_APP=view_schedule.py && export FLASK_ENV=development && export FLASK_DEBUG=1 && flask run --port 5100"

open -a Terminal.app -n --args bash -c "export FLASK_APP=view_requests.py && export FLASK_ENV=development && export FLASK_DEBUG=1 && flask run --port 5101"

open -a Terminal.app -n --args bash -c "export FLASK_APP=view_requests.py && export FLASK_ENV=development && export FLASK_DEBUG=1 && flask run --port 5102"

open -a Terminal.app -n --args bash -c "export FLASK_APP=view_requests.py && export FLASK_ENV=development && export FLASK_DEBUG=1 && flask run --port 5003"
