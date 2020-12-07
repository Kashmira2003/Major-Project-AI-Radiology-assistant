import pytest

from radiology_assistant import create_app, db
from radiology_assistant.models import *

@pytest.fixture
def app():
    app = create_app()

    app.config["TESTING"] = True
    app.testing = True

    app.config["WTF_CSRF_ENABLED"] = False

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

    with app.app_context():
        db.create_all()
    
    yield app

@pytest.fixture
def test_client(app):
    return app.test_client()
