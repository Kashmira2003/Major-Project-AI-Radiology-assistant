import pytest
from radiology_assistant.tests import test_client, app
from flask import current_app
import os
from flask_wtf.file import FileStorage


class TestUploadingImages:

    def test_upload_image(self, test_client, app):
        # upload an image, make sure its in temp
        with app.app_context():

            f = FileStorage(filename="radiology_assistant/tests/sample_xray.jpg", stream=open("radiology_assistant/tests/sample_xray.jpg", "rb"), content_type="image/jpeg")
            test_client.post("/", data=dict(image=f), content_type="multipart/form-data")
            assert len(os.listdir(os.path.join(current_app.root_path, current_app.static_folder, "images", "temp"))) != 0
