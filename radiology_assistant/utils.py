import os
import uuid
from flask import current_app, session
from PIL import Image, ImageChops
import time
from radiology_assistant import db
import random
import shutil
import multiprocessing
from radiology_assistant.models import Case
from radiology_assistant import create_app
from config import Config
import numpy as np
import cv2
import socket
from flask import render_template


class UserSession:
    '''
    Wrapper class around the flask session.

    Provides utilities for uploading images and saving detected diseases for the user's current session on the site.
    '''

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
        
        # here are the RGB changes
        rgb_img = Image.new("RGB", p_img.size)
        rgb_img.paste(p_img)
        rgb_img.save(img_path)
        
        session[cls._session_image_string] = img_name

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

def convert_to_bytes(no):
    result = bytearray()
    result.append(no & 255)
    for i in range(3):
        no = no >> 8
        result.append(no & 255)
    return result

def bytes_to_number(b):
    # if Python2.x
    # b = map(ord, b)
    res = 0
    for i in range(4):
        res += b[i] << (i*8)
    return res

# def get_model_results(img):
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
#             port = 5061
#             s.connect((socket.gethostname(), port))

#             file = UserSession.get_uploaded_image(full_path=2)
#             f = open(file, 'rb')
#             f = f.read()

#             length = convert_to_bytes(len(f))
#             s.send(length)
#             s.send(f)

#             print("awaiting results...")
#             size = s.recv(4)

#             result = s.recv(bytes_to_number(size))
#             print(result)
#             s.close()
#     return result


def get_model_results(img):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            port = 5061
            s.connect(('127.0.0.1', port))  # Make sure model server is running here

            file = UserSession.get_uploaded_image(full_path=2)
            with open(file, 'rb') as f:
                file_data = f.read()

            length = convert_to_bytes(len(file_data))
            s.send(length)
            s.send(file_data)

            print("Awaiting results...")
            size = s.recv(4)
            result_size = bytes_to_number(size)
            result = s.recv(result_size)

            print("Received results:", result)
            return result
    except Exception as e:
        print(f"Error connecting to detection model: {e}")
        return "Error: Could not connect to model server. Please try again later."



# def model(img):
#     # this function can be edited as necessary
#     # it accepts the image path as a parameter
#     # it should return a list of tuples, where each entry is (disease_name, percentage) where percentage is a float between 0 and 1
#     diseases = ['Fracture', 'Pneumothorax', 'Airspace opacity', 'Nodule or mass', 'Disease not detected']
#     results = str(get_model_results(img))
#     time.sleep(2)
#     detected = []
#     for i in diseases:
#         if i in results:
#             detected.append(i)

#     #count = 0
#     #for i in test_str: 
#     #    if i == '0.': 
#     #        count = count + 1

#     percentages = [random.uniform(0.1,0.99) for _ in detected]

#     return list(zip(detected, percentages))



def model(img):
    # Print statement to confirm the model was called and with what image
    print("Running disease detection on image:", img)
    
    # this function can be edited as necessary
    diseases = ['Fracture', 'Pneumothorax', 'Airspace opacity', 'Nodule or mass', 'Disease not detected']
    
    # Get the result from the socket-based model
    results = str(get_model_results(img))
    print("Raw model results:", results)  # Debug statement

    time.sleep(2)
    detected = []
    for disease in diseases:
        if disease in results:
            detected.append(disease)

    percentages = [random.uniform(0.1, 0.99) for _ in detected]
    predictions = list(zip(detected, percentages))
    
    print("Predictions generated:", predictions)  # Debug statement
    return predictions


# extra added code
# Assuming this part calls the model for disease detection
def perform_detection():
    img = UserSession.get_uploaded_image(full_path=2)
    predictions = model(img)  # Run the model to get predictions

    # Save the predictions in the session
    UserSession.set_detected_results(predictions)
    
    # Debug: Confirm results are saved
    print("Detection results saved in session:", session.get(UserSession._session_results_string))
    return predictions


def generate_report():
    # Retrieve the prediction from the session
    prediction = UserSession.get_detected_results()

    # Display an error if no detection has been made
    if not prediction:
        return "No prediction available. Please run detection first."

    # Create the report based on the prediction
    report = f"Detected Diseases: {prediction}"
    print(report)  # Debug statement to check report content

    # Render this in your template
    return render_template('report.html', prediction=prediction)



def dump_temp():
    # temp = os.path.join(current_app.root_path, "static", "images", "temp")
    # for f in os.listdir(temp):
    #     os.remove(os.path.join(temp, f))
    temp = os.path.join(current_app.root_path, "static", "images", "temp")
    
    # Check if the directory exists
    if os.path.exists(temp):
        for f in os.listdir(temp):
            os.remove(os.path.join(temp, f))
    else:
        # If the directory doesn't exist, create it
        os.makedirs(temp)



def run_duplication_deletion(constant=False):
    if constant:
        print("Running constant duplication deletion...")
        multiprocessing.Process(target=background_deletion, daemon=True).start()
    else:
        print("Running manual duplication deletion...")
        multiprocessing.Process(target=delete_duplicates).start()


def background_deletion():
    while True:
        delete_duplicates()
        time.sleep(Config.MINUTES_BETWEEN_DUPLICATE_DELETION)


def delete_duplicates():
    app = create_app()
    with app.app_context():
        path = os.path.join(current_app.root_path, "static", "images", "xrays")

        for f in os.listdir(path):
            # in case we reach a file we already deleted
            if not os.path.exists(os.path.join(path, f)):
                continue
            # if an image doesn't belong to a case
            elif not Case.query.filter_by(image=f).first():
                os.remove(os.path.join(path, f))
                continue

            img1 = Image.open(os.path.join(path, f))
            for f2 in os.listdir(path):
                if f != f2:
                    img2 = Image.open(os.path.join(path, f2))
                    try:
                        diff = ImageChops.difference(img1, img2)
                        if not diff.getbbox():
                            case = Case.query.filter_by(image=f2).first()
                            if case:
                                db.session.delete(case)
                                db.session.commit()
                                os.remove(os.path.join(path, f2))
                    except ValueError:
                        continue


