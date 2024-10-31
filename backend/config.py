import os


"""
Can be used to set configuration variables for the Flask app.

app = Flask(__name__)
app.config.from_object('config.Config')
"""


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 299}
    CORS_ORIGINS = "*"
    DEBUG = True
    TESTING = True
