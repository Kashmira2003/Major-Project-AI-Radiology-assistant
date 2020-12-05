from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

class ImageUploadForm(FlaskForm):
    image = FileField("", validators=[FileRequired(), FileAllowed(["jpg", "png"])])

class MedicalReportForm(FlaskForm):
    patient_name = StringField('Patient Name', validators=[DataRequired(), Length(min=2, max=50)])
    additional_diseases = StringField('Enter Additional Diseases (Comma Seperated)', validators=[])
    additional_details = TextAreaField('Enter Additional Details')
    submit = SubmitField('Generate Report')
