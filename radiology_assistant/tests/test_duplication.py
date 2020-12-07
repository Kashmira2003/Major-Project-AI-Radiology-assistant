from genericpath import exists
import pytest
from radiology_assistant.tests import test_client, app
from radiology_assistant import db
from radiology_assistant.models import User, Case
import os
import shutil
from flask import current_app
from radiology_assistant.utils import delete_duplicates

class TestDuplicationDetection:

    def test_duplicate_removal(self, test_client, app):
        test_client.post("/register", data=dict(firstname="Test", lastname="User", username="testuser", email="testuser@test.com", password="test", confirm_password="test"))
        with app.app_context():
            user = User.query.filter_by(username="testuser").first()
            shutil.copy2("radiology_assistant/tests/sample_xray.jpg", os.path.join(current_app.root_path, current_app.static_folder, "images", "xrays", "xray1.jpg"))
            shutil.copy2("radiology_assistant/tests/sample_xray.jpg", os.path.join(current_app.root_path, current_app.static_folder, "images", "xrays", "xray2.jpg"))
            c1 = Case(image="xray1.jpg", patient="Test Patient", details="Test Details", user_id=user.id)
            c2 = Case(image="xray2.jpg", patient="Test Patient 2", details="Test Details 2", user_id=user.id)
            db.session.add(c1)
            db.session.add(c2)
            db.session.commit()
            delete_duplicates()
            assert (os.path.exists(os.path.join(current_app.root_path, current_app.static_folder, "images", "xrays", "xray1.jpg"))) and (not os.path.exists(os.path.join(current_app.root_path, current_app.static_folder, "images", "xrays", "xray2.jpg")))


