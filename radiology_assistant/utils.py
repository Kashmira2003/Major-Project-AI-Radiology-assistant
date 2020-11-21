import os
import uuid
from flask import current_app, session
from PIL import Image
import threading
import time
from radiology_assistant import app
import random
import shutil

class UserSession:
    '''
    Wrapper class around the flask session.

    Provides utilities for uploading images and saving detected diseases for the user's current session on the site.
    '''

    _upload_time = 600
    _session_image_string = "user_image"
    _session_results_string = "detection_results"
    _temp_image_path = os.path.join("images", "temp")
    _permanent_xray_path = os.path.join("images", "xrays")

    @classmethod
    def set_uploaded_image(cls, img):
        '''
        Saves a user's uploaded image to the server.

        Calling this erases any currently existing user image or results.
        '''
        img_id = uuid.uuid4().hex
        _, img_ext = os.path.splitext(img.filename)
        img_name = img_id + img_ext
        img_path = os.path.join(current_app.root_path, current_app.static_folder, cls._temp_image_path, img_name)
        print(img_path)
        p_img = Image.open(img)
        p_img.save(img_path)
        session[cls._session_image_string] = img_name
        # threading.Thread(target=schedule_img_delete, args=(img_name, UserSession.upload_time, app), daemon=True).start()

    @classmethod
    def get_uploaded_image(cls, full_path=0):
        '''
        Returns the directory for the user uploaded image, or None if no image exists.

        If full_path=0, only the image name is returned.

        If full_path=1, Return format is as follows: "images/temp/image_id.format"
         
        If full_path=2, "path/to/current/app/static/" is included at the start of the path as well.
        '''
        user_image = session.get(cls._session_image_string)
        img_path = os.path.join(current_app.root_path, current_app.static_folder, cls._temp_image_path, user_image)
        if user_image is not None and os.path.exists(img_path):
            if full_path == 0:
                return user_image
            elif full_path == 1:
                return os.path.join(cls._temp_image_path, user_image)
            elif full_path == 2:
                return img_path


    @classmethod
    def finalize_image(cls):
        '''
        Moves the current user image into the site's permanantly saved xrays.
        '''
        image_name = cls.get_uploaded_image()
        image_path = cls.get_uploaded_image(full_path=2)

        new_path = os.path.join(current_app.root_path, current_app.static_folder, cls._permanent_xray_path, image_name)
        shutil.copy2(image_path, new_path)
        os.remove(image_path)

    @classmethod
    def set_detected_results(cls, results):
        '''
        Saves the results of a detection.
        '''
        session[cls._session_results_string] = results

    @classmethod
    def get_detected_results(cls):
        '''
        Get the saved results of a detection.
        '''
        return session.get(cls._session_results_string)


def schedule_img_delete(img, secs, cur_app):
    time.sleep(secs)
    try:
        with cur_app.app_context():
            os.remove(os.path.join(cur_app.root_path, "static", "images", "temp", img))
    except Exception as e:
        print(e)
        pass

def save_temp_image(img, secs):
    img_id = uuid.uuid4().hex
    _, img_ext = os.path.splitext(img.filename)
    img_name = img_id + img_ext
    img_path = os.path.join(current_app.root_path, "static", "images", "temp", img_name)

    p_img = Image.open(img)
    p_img.save(img_path)
    session["temp_image"] = img_name
    threading.Thread(target=schedule_img_delete, args=(img_name, secs, app), daemon=True).start()
    return img_name

def image_in_temp():
    temp_image = session.get("temp_image")
    if temp_image is None:
        return False
    else:
        return os.path.exists(os.path.join(current_app.root_path, "static", "images", "temp", temp_image))




def model(img):
    diseases = ["Cardiomegaly", "Emphysema", "Effusion", "Hernia", "Infiltration", "Mass", "Nodule", "Atelectasis", "Pneumothorax", "Pleural_Thickening"]
    time.sleep(2)
    num_diseases = random.randint(0, 4)
    detected = random.sample(diseases, num_diseases)
    percentages = [random.uniform(0.1,0.99) for _ in detected]

    return list(zip(detected, percentages))



def dump_temp():
    temp = os.path.join(current_app.root_path, "static", "images", "temp")
    for f in os.listdir(temp):
        os.remove(os.path.join(temp, f))