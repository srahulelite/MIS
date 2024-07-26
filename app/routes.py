# app/routes.py

from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db
from flask_bcrypt import Bcrypt 
from app.forms import RegistrationForm, LoginForm, TimesheetEntryForm
from app.models import User, Project, Task, TimesheetEntry


bcrypt = Bcrypt(app)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/timesheet', methods=['GET', 'POST'])
@login_required
def timesheet():
    form = TimesheetEntryForm()
    form.project_id.choices = [(project.id, project.name) for project in Project.query.all()]
    form.task_id.choices = [(task.id, task.name) for task in Task.query.all()]
    if form.validate_on_submit():
        entry = TimesheetEntry(user_id=current_user.id, project_id=form.project_id.data, task_id=form.task_id.data, hours=form.hours.data)
        db.session.add(entry)
        db.session.commit()
        flash('Timesheet entry added!', 'success')
        return redirect(url_for('timesheet'))
    return render_template('timesheet_entry.html', title='Timesheet Entry', form=form)
