from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('config.Config')
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
        db.Integer, db.ForeignKey('employee.staff_id'), nullable=True)
    role = db.Column(db.Integer, nullable=False)

    def __init__(self, staff_id, staff_fname, staff_lname, dept, position, country, email, role, reporting_manager=None):
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
            "role": self.role
        }


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
        employee = db.session.query(Employee).filter_by(
            staff_id=staff_id).first()
        if employee:
            return jsonify(
                {
                    "code": 200,
                    "data": employee.json()
                }
            )

    except Exception as e:
        return jsonify({
            "code": 404,
            "error": "Employee not found. " + str(e)
        }), 404


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
            return jsonify({
                "code": 404,
                "message": f"No staff found reporting to manager with ID {staff_id}."
            }), 404

        # Serialize the list of employees
        staff_data = [staff.json() for staff in staff_list]

        return jsonify({
            "code": 200,
            "data": staff_data
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "error": "An error occurred while fetching staff data. " + str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
