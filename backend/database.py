from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


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


class Request(db.Model):
    __tablename__ = "request"

    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    staff_id = db.Column(db.Integer, db.ForeignKey("employee.staff_id"), nullable=False)
    creation_date = db.Column(db.Date, nullable=False)
    apply_reason = db.Column(db.String(100), nullable=False)
    reject_reason = db.Column(db.String(100), nullable=True)

    def __init__(
        self, staff_id, creation_date, apply_reason, reject_reason=None, request_id=None
    ):
        self.request_id = request_id
        self.staff_id = staff_id
        self.creation_date = creation_date
        self.apply_reason = apply_reason
        self.reject_reason = reject_reason

    def json(self):
        return {
            "request_id": self.request_id,
            "staff_id": self.staff_id,
            "creation_date": self.creation_date.isoformat(),
            "apply_reason": self.apply_reason,
            "reject_reason": self.reject_reason,
        }


class RequestDates(db.Model):
    __tablename__ = "request_dates"

    request_date_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(
        db.Integer, db.ForeignKey("request.request_id"), nullable=False
    )
    request_date = db.Column(db.Date, nullable=False)
    request_shift = db.Column(db.String(5), nullable=False)
    request_status = db.Column(db.String(20), nullable=False)
    rescind_reason = db.Column(db.String(100), nullable=True)
    withdraw_reason = db.Column(db.String(100), nullable=True)

    def __init__(
        self,
        request_id,
        request_date,
        request_shift,
        request_date_id=None,
        request_status="Pending Approval",
        withdraw_reason=None,
        rescind_reason=None,
    ):
        self.request_date_id = request_date_id
        self.request_id = request_id
        self.request_date = request_date
        self.request_shift = request_shift
        self.request_status = request_status
        self.rescind_reason = rescind_reason
        self.withdraw_reason = withdraw_reason

    def json(self):
        return {
            "request_date_id": self.request_date_id,
            "request_id": self.request_id,
            "request_date": self.request_date.isoformat(),
            "request_shift": self.request_shift,
            "request_status": self.request_status,
            "withdraw_reason": self.withdraw_reason,
            "rescind_reason": self.rescind_reason,
        }


class StatusLog(db.Model):
    __tablename__ = "Status_Log"

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(
        db.Integer, db.ForeignKey("request.request_id"), nullable=False
    )
    log_date = db.Column(db.DateTime, default=datetime.now)
    action = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.String(100), nullable=True)

    request = db.relationship("Request", backref="status_logs")

    def __init__(self, request_id, action, reason=None):
        self.request_id = request_id
        self.action = action
        self.reason = reason

    def json(self):
        return {
            "log_id": self.log_id,
            "request_id": self.request_id,
            "log_date": self.log_date.isoformat(),
            "action": self.action,
            "reason": self.reason,
        }
