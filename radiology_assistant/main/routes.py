from sys import path
from radiology_assistant.main import main
from radiology_assistant import db
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
from radiology_assistant.models import Case, Disease
from radiology_assistant.main.forms import ImageUploadForm, MedicalReportForm
from radiology_assistant.utils import model, UserSession

@main.route("/", methods=['GET', 'POST'])
def home():
    form = ImageUploadForm()
    if form.is_submitted():
        if form.validate():
            # save_temp_image(form.image.data, 600)
            UserSession.set_uploaded_image(form.image.data)
            return redirect(url_for("main.confirm"))
        else:
            flash("Something went wrong. Please make sure you uploaded either a .png or .jpg image.", "danger")
    return render_template("home.html", form=form)

@main.route("/confirm", methods=['GET', 'POST'])
def confirm():
    user_image_name = UserSession.get_uploaded_image()
    if user_image_name is None:
        flash("You can't confirm an image until you upload an image!", "danger")
        return redirect(url_for("main.home"))
    else:
        return render_template("confirmation.html", img_name=user_image_name)


@main.route("/results", methods=['GET', 'POST'])
def results():
    user_image_name = UserSession.get_uploaded_image()
    if user_image_name is None:
        flash("Session timed out. Please upload another image.", "danger")
        return redirect(url_for("main.home"))

    form = MedicalReportForm()
    if request.method == "POST":
        if form.validate_on_submit():
            UserSession.finalize_image()
            results = UserSession.get_detected_results()
            case = Case(image=user_image_name, patient=form.patient_name.data, details=form.additional_details.data, user=current_user)
            db.session.add(case)
            for disease, percentage in results:
                d = Disease(case=case, name=disease, percentage=percentage)
                db.session.add(d)

            for disease in form.additional_diseases.data.split(","):
                d = Disease(case=case, name=disease.strip(" "))
                db.session.add(d)

            db.session.commit()
            return redirect(url_for("main.report", report_id=case.id))

    elif request.method == "GET":
        # here is where the image name gets passed to the dummy model
        # path=2 in the get_uploaded_image function gives the whole path to the image along with its name
        # read the docstring on it for more info
        results = model(UserSession.get_uploaded_image(path=2))
        UserSession.set_detected_results(results)
        results = [(disease, int(pct*100)) for disease, pct in results]
        summary = ""
        for x in range(len(results)):
            if x != 0:
                if x == (len(results)-1) and x != 0:
                    summary += "and "
            if str(results[x][0]) == "Nodule":
                if results[x][1] < 15:
                    summary += str("Presence of few" + results[x][0] + "s")
                else:
                    summary += str("Presence of many" + results[x][0] + "s")
            elif str(results[x][0]) == "Mass":
                if results[x][1] < 15:
                    summary += str("Presence of a small or few small Masses")
                else:
                    summary += str("Presence of one large or several small Masses")
            elif str(results[x][0]) == "Hernia":
                if results[x][1] < 15:
                    summary += str("Atypical/showing signs of a " + results[x][0])
                elif results[x][1] < 25:
                    summary += str("Acute symptoms of a " + results[x][0])
                elif results[x][1] < 65:
                    summary += str("Moderate symptoms of a " + results[x][0])
                else:
                    summary += str("Severe symptoms of a " + results[x][0])
            else:
                if results[x][1] < 15:
                    summary += str("Atypical/showing signs of " + results[x][0])
                elif results[x][1] < 25:
                    summary += str("Acute symptoms of " + results[x][0])
                elif results[x][1] < 65:
                    summary += str("Moderate symptoms of " + results[x][0])
                else:
                    summary += str("Severe symptoms of " + results[x][0])                
            if x < (len(results)-1):
                summary += ", "
        form.additional_details.data=summary
        return render_template("results.html", image=user_image_name, results=results, user_auth=current_user.is_authenticated, form=form)

@main.route("/report/<int:report_id>")
def report(report_id):
    case = Case.query.filter_by(id=report_id).first_or_404()
    detected = []
    additional = []
    for disease in case.diseases:
        if disease.percentage is None:
            additional.append(disease)
        else:
            detected.append(disease)
    return render_template("report.html", case=case, detected=detected, additional=additional)