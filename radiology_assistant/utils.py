
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


def run_duplication_deletion(constant=False):
    if constant:
        multiprocessing.Process(target=background_deletion, daemon=True).start()
    else:
        multiprocessing.Process(target=delete_duplicates).start()

def background_deletion():
    while True:
        delete_duplicates()
        time.sleep(1800)

def delete_duplicates():
    app = create_app()
    with app.app_context():
        path = os.path.join(current_app.root_path, "static", "images", "xrays")

        for f in os.listdir(path):
            # in case we reach a file we already deleted
            if not os.path.exists(os.path.join(path, f)):
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
