from flask import Flask, request, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from run import db

app = Blueprint("employee", __name__)
# app.config.from_object("config.Config")
# db = SQLAlchemy(app)
CORS(app)


class Employee(db.Model):
    __tablename__ = "employee"

    staff_id = db.Column(db.Integer, primary_key=True)
    staff_fname = db.Column(db.String(50), nullable=False)
    staff_lname = db.Column(db.String(50), nullable=False)
    dept = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    reporting_manager = db.Column(
        db.Integer, db.ForeignKey("employee.staff_id"), nullable=True
    )
    role = db.Column(db.Integer, nullable=False)

    def __init__(
        self,
        staff_id,
        staff_fname,
        staff_lname,
        dept,
        position,
        country,
        email,
        role,
        reporting_manager=None,
    ):
        self.staff_id = staff_id
        self.staff_fname = staff_fname
        self.staff_lname = staff_lname
        self.dept = dept
        self.position = position
        self.country = country
        self.email = email
        self.reporting_manager = reporting_manager
        self.role = role

    def json(self):
        return {
            "staff_id": self.staff_id,
            "staff_fname": self.staff_fname,
            "staff_lname": self.staff_lname,
            "dept": self.dept,
            "position": self.position,
            "country": self.country,
            "email": self.email,
            "reporting_manager": self.reporting_manager,
            "role": self.role,
        }


@app.route("/")
def hello():
    return "This is employee.py"


@app.route("/get_details/<int:staff_id>", methods=["GET"])
def get_employee_details(staff_id):
    """
    Get employee details based on id
    ---
    Parameters:
        staff_id (int): The staff_id

    Success response:
        {
            "code": 200,
            "data": {
                "staff_id": 1,
                "staff_fname": "John",
                "staff_lname": "Doe",
                "dept": "IT",
                "position": "Developer",
                "country": "USA",
                "email": "john.doe@example.com",
                "reporting_manager": 1,
                "role": 1
            }
        }
    """
    try:
        employee = Employee.query.get(staff_id)
        if employee:
            return jsonify({"code": 200, "data": employee.json()})
        return jsonify({"code": 404, "error": "Employee not found."}), 404
    except Exception as e:
        return jsonify({"code": 500, "error": f"An error occurred: {e}"}), 500


@app.route("/get_staff/<int:staff_id>", methods=["GET"])
def get_staff_by_manager(staff_id):
    """
    Get the list of employees who report to a specific manager based on staff_id
    ---
    Parameters:
        staff_id (int): The manager's staff_id

    Success response:
        {
            "code": 200,
            "data": [
                {
                    "country": "Singapore",
                    "dept": "Sales",
                    "email": "Susan.Goh@allinone.com.sg",
                    "position": "Account Manager",
                    "reporting_manager": 140894,
                    "role": 2,
                    "staff_fname": "Susan",
                    "staff_id": 140002,
                    "staff_lname": "Goh"
                },
                ...
            ]
        }
    """
    try:
        staff_list = Employee.query.filter_by(reporting_manager=staff_id).all()
        if staff_list:
            staff_data = [staff.json() for staff in staff_list]
            return jsonify({"code": 200, "data": staff_data}), 200
        return (
            jsonify(
                {
                    "code": 404,
                    "message": f"No staff found reporting to manager with ID {staff_id}.",
                }
            ),
            404,
        )
    except Exception as e:
        return jsonify({"code": 500, "error": f"An error occurred: {e}"}), 500


@app.route("/get_team/<int:staff_id>", methods=["GET"])
def get_team(staff_id):
    """
    Get the list of employees who report to a specific manager based on staff_id
    ---
    Parameters:
        staff_id (int): The manager's staff_id

    Success response:
        {
            "director_id": 140001,
            "managers_and_teams": [
                {
                    "manager_id": 140008,
                    "team_members": [
                        140008,
                        140880
                    ]
                },
                {
                    "manager_id": 140103,
                    "team_members": [
                        140103,
                        140893
                    ]
                },...
            ]
        }
    """
    try:
        staff_list = Employee.query.filter_by(reporting_manager=staff_id).all()
        output = {"director_id": staff_id, "managers_and_teams": []}

        for manager in staff_list:
            team_members = [
                member.staff_id
                for member in Employee.query.filter_by(
                    reporting_manager=manager.staff_id
                ).all()
            ]
            team = {
                "manager_id": manager.staff_id,
                "team_members": [manager.staff_id] + team_members,
            }
            output["managers_and_teams"].append(team)

        return jsonify(output), 200
    except Exception as e:
        return jsonify({"code": 500, "error": f"An error occurred: {e}"}), 500


@app.route("/get_all_employees", methods=["GET"])
def get_all_employees():
    """
    Get all staff IDs and their reporting managers.

    Success response:
    {
        "code": 200,
        "data": [
            {
                "staff_id": 150001,
                "reporting_manager": 150111,
                "staff_name": "Tan Wei Ming",
                "dept": "Finance",
                "position": "Associate"
            },
            {
                "staff_id": 150002,
                "reporting_manager": 150111,
                "staff_name": "Lim Hong Wei",
                "dept": "Sales",
                "position": "Associate"
            },
            ...
        ]
    }
    """
    try:
        employees = Employee.query.all()
        reporting_structure = [
            {
                "staff_id": employee.staff_id,
                "reporting_manager": employee.reporting_manager,
                "staff_name": f"{employee.staff_fname} {employee.staff_lname}",
                "dept": employee.dept,
                "position": employee.position,
            }
            for employee in employees
        ]
        return jsonify({"code": 200, "data": reporting_structure}), 200
    except Exception as e:
        return jsonify({"code": 500, "error": f"An error occurred: {e}"}), 500


@app.route("/get_all_employees_by_dept", methods=["GET"])
def get_all_employees_by_dept():
    """
    Get all staff IDs and their details, grouped by department.

    Success response:
    {
        "code": 200,
        "data": {
            "Engineering": {
                "150488": {
                    "staff_name": "Jacob Tan",
                    "role": "Junior Engineer",
                    "staff_id": 150488,
                    "reporting_manager": 150111
                },
                "104821": {
                    "staff_name": "James Teo",
                    "role": "Junior Engineer",
                    "staff_id": 104821,
                    "reporting_manager": 150111
                },
            },
            "Sales": { ... },
        }
    }
    """
    try:
        employees = Employee.query.all()
        reporting_structure = {}

        for employee in employees:
            dept = employee.dept
            staff_data = {
                "staff_name": f"{employee.staff_fname} {employee.staff_lname}",
                "role": employee.position,
                "staff_id": employee.staff_id,
                "reporting_manager": employee.reporting_manager,
            }
            reporting_structure.setdefault(dept, {})[employee.staff_id] = staff_data

        return jsonify({"code": 200, "data": reporting_structure}), 200
    except Exception as e:
        return jsonify({"code": 500, "error": f"An error occurred: {e}"}), 500


# if __name__ == "__main__":
#     app.run()
