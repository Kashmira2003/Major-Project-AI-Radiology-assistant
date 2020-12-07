import pytest
from radiology_assistant.tests import test_client, app
from radiology_assistant.models import Case, User, Disease
from radiology_assistant import db

class TestSearch:

    def test_existing_search(self, test_client, app):
        test_client.post("/register", data=dict(firstname="Test", lastname="User", username="testuser", email="testuser@test.com", password="test", confirm_password="test"))
        with app.app_context():
            user = User.query.filter_by(username="testuser").first()
            c = Case(image="xray1.jpg", patient="Test Patient", details="Test Details", user_id=user.id)
            d = Disease(case=c, name="Test")
            db.session.add(c)
            db.session.add(d)
            db.session.commit()

        result = test_client.get("/search", query_string=dict(query="Test"))
        assert "No Results found" not in str(result.data)   

    def test_nonexisting_search(self, test_client):
        result = test_client.get("/search", query_string=dict(query="nonexistant_disease"))
        assert "No Results found" in str(result.data)