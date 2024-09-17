from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)


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


@app.route("/employee/<int:staff_id>")
def get_employee_details(staff_id):
    """
    Get employee details based on id
    ---
    responses:
        200:
            description: Return employee
        404:
            description: Unable to find employee
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
