import os


"""
Can be used to set configuration variables for the Flask app.

app = Flask(__name__)
app.config.from_object('config.Config')
"""


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'dbURL') or 'mysql+mysqlconnector://root@localhost:3306/wfh_scheduling'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 299}
    CORS_ORIGINS = "*"
