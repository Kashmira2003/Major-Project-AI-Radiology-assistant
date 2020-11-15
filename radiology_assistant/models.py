from datetime import datetime
from radiology_assistant import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    cases = db.relationship('Case', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.firstname} {self.lastname}, {self.username}', '{self.email}')"

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(36), nullable=False, unique=True)
    patient = db.Column(db.String(50), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    details = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    diseases = db.relationship('Disease', backref='case', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"Case('{self.id}', '{self.date_posted}')"

class Disease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    percentage = db.Column(db.Float)

    def __repr__(self):
        return f"Disease('{self.name}', '{self.case_id}')"

db.create_all()