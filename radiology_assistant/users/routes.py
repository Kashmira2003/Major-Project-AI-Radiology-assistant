from radiology_assistant.users import users
from radiology_assistant import bcrypt, db
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from radiology_assistant.models import User
from radiology_assistant.users.forms import AdminForm, RegistrationForm, LoginForm, UpdateAccountForm
from radiology_assistant.utils import run_duplication_deletion

@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(firstname=form.firstname.data, lastname=form.lastname.data, username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You may now log in.', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check username and password and try again.', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route("/account/admin", methods=['GET', 'POST'])
@login_required
def admin():
    form = AdminForm()
    if form.validate_on_submit():
        run_duplication_deletion(constant=False)
        flash("Duplication Deletion started.", "success")
        return redirect(url_for("main.home"))

    return render_template("admin.html", form=form)

@users.route("/account/cases")
@login_required
def user_cases():
    return render_template("user_cases.html", cases=current_user.cases)

@users.route("/account/settings", methods=['GET', 'POST'])
@login_required
def account_settings():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        if len(form.password.data) > 0:
            current_user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') 
        db.session.commit()
        flash("Your account settings have been updated.", "success")
        return redirect(url_for("main.home"))
    elif request.method == "GET":
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template("settings.html", form=form)