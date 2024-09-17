from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
from request import Request

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get(
    'dbURL') or 'mysql+mysqlconnector://root:root@localhost:3306/wfh_scheduling'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)
CORS(app, resources={r"/*": {"origins": "*"}})


class Request_Dates(db.Model):
    __tablename__ = "request"

    request_date_id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey(
        'request.request_id'), nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    request_status = db.Column(db.String(20), nullable=False)

    def __init__(self, request_date_id, request_id, request_date, request_status):
        self.request_date_id = request_date_id
        self.request_id = request_id
        self.request_date = request_date
        self.request_status = request_status

    def json(self):
        return {
            "request_date_id": self.request_date_id,
        }
