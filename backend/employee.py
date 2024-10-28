from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object("config.Config")
db = SQLAlchemy(app)
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


# Retrieve details of an employee
@app.route("/employee/get_details/<int:staff_id>")
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
        employee = db.session.query(Employee).filter_by(staff_id=staff_id).first()
        if employee:
            return jsonify({"code": 200, "data": employee.json()})

    except Exception as e:
        return jsonify({"code": 404, "error": "Employee not found. " + str(e)}), 404


# Retrieve details of employees under an employee/user
@app.route("/employee/get_staff/<int:staff_id>")
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
        # Fetch employees where reporting_manager matches the provided staff_id
        staff_list = Employee.query.filter_by(reporting_manager=staff_id).all()

        if not staff_list:
            return (
                jsonify(
                    {
                        "code": 404,
                        "message": f"No staff found reporting to manager with ID {staff_id}.",
                    }
                ),
                404,
            )

        # Serialize the list of employees
        staff_data = [staff.json() for staff in staff_list]

        return jsonify({"code": 200, "data": staff_data}), 200

    except Exception as e:
        return (
            jsonify(
                {
                    "code": 500,
                    "error": "An error occurred while fetching staff data. " + str(e),
                }
            ),
            500,
        )


# Retrieve all employees
@app.route("/employee/get_all_employees", methods=["GET"])
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
        # Fetch all employees
        employees = Employee.query.all()

        # Prepare the data
        reporting_structure = [
            {
                "staff_id": employee.staff_id,
                "reporting_manager": employee.reporting_manager,
                "staff_name": employee.staff_fname + " " + employee.staff_lname,
                "dept": employee.dept,
                "position": employee.position,
            }
            for employee in employees
        ]

        return jsonify({"code": 200, "data": reporting_structure}), 200

    except Exception as e:
        return (
            jsonify(
                {
                    "code": 500,
                    "error": "An error occurred while fetching reporting structure. "
                    + str(e),
                }
            ),
            500,
        )


# Retrieve employees, grouped by department
@app.route("/employee/get_all_employees_by_dept", methods=["GET"])
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
        # Fetch all employees
        employees = Employee.query.all()

        # Prepare the data grouped by department
        reporting_structure = {}

        for employee in employees:
            dept = employee.dept
            staff_id = employee.staff_id

            # Initialize department if it doesn't exist in the structure
            if dept not in reporting_structure:
                reporting_structure[dept] = {}

            # Add employee data under the specific department and staff_id
            reporting_structure[dept][staff_id] = {
                "staff_name": employee.staff_fname + " " + employee.staff_lname,
                "role": employee.position,
                "staff_id": employee.staff_id,
                "reporting_manager": employee.reporting_manager,
            }

        return jsonify({"code": 200, "data": reporting_structure}), 200

    except Exception as e:
        return (
            jsonify(
                {
                    "code": 500,
                    "error": "An error occurred while fetching reporting structure. "
                    + str(e),
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
