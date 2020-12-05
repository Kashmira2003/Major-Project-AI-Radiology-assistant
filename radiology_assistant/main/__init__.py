from flask import Blueprint

main = Blueprint("main", __name__)

from radiology_assistant.main import routes
