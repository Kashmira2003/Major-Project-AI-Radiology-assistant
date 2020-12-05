from flask import Blueprint

search = Blueprint("search", __name__)

from radiology_assistant.search import routes
