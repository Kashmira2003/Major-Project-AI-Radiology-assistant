from flask import Blueprint

users = Blueprint("users", __name__)

from radiology_assistant.users import routes

