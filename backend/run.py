from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

# Create a new Flask app to serve as the main entry point
app = Flask(__name__)
CORS(app)

# Set up the database
app.config.from_object("config.Config")
db = SQLAlchemy(app)
# db.init_app(app)

# Import your Flask apps
from employee import app as employee_app
from request import app as request_app
from request_dates import app as request_dates_app
from view_requests import app as view_requests_app
from reject_requests import app as reject_requests_app
from status_log import app as status_log_app
from view_schedule import app as view_schedule_app


# Register blueprints or routes from your individual apps
app.register_blueprint(employee_app, url_prefix="/employee")
app.register_blueprint(request_app, url_prefix="/request")
app.register_blueprint(request_dates_app, url_prefix="/request_dates")
app.register_blueprint(view_requests_app, url_prefix="/view_requests")
app.register_blueprint(reject_requests_app, url_prefix="/reject_requests")
app.register_blueprint(status_log_app, url_prefix="/status_log")
app.register_blueprint(view_schedule_app, url_prefix="/view_schedule")


@app.route("/")
def index():
    return "Welcome to the WFH Scheduling API"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
