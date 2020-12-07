import pytest
from radiology_assistant.models import User
from radiology_assistant.tests import test_client, app

class TestRegistration:

    def test_create_account(self, test_client, app):
        test_client.post("/register", data=dict(firstname="Test", lastname="User", username="testuser", email="testuser@test.com", password="test", confirm_password="test"))
        with app.app_context():
            user = User.query.filter_by(username="testuser").first()
            assert user is not None

    def test_create_existing_account(self, test_client):
        test_client.post("/register", data=dict(firstname="Test", lastname="User", username="testuser", email="testuser@test.com", password="test", confirm_password="test"))
        result = test_client.post("/register", data=dict(firstname="Test", lastname="User", username="testuser", email="testuser@test.com", password="test", confirm_password="test"))
        # Status code 200 means user wasn't redirected which means error logging in
        assert result.status_code == 200

    def test_correct_login(self, test_client):
        test_client.post("/register", data=dict(firstname="Test", lastname="User", username="testuser", email="testuser@test.com", password="test", confirm_password="test"))
        result = test_client.post("/login", data=dict(username="testuser", password="test"))
        assert result.status_code == 302

    def test_incorrect_login(self, test_client):
        result = test_client.post("/login", data=dict(username="bogususername", password="randompassword"))
        assert result.status_code == 200

    def test_update_account(self, test_client, app):
        test_client.post("/register", data=dict(firstname="Test", lastname="User", username="testuser", email="testuser@test.com", password="test", confirm_password="test"))
        test_client.post("/login", data=dict(username="testuser", password="test"))
        test_client.post("/account/settings", data=dict(firstname="Test2", lastname="User2", username="testuser2", email="testuser2@test.com"))
        with app.app_context():
            user = User.query.filter_by(username="testuser2").first()
            assert user is not None

        
