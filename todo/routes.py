from flask import render_template, redirect, url_for, flash, request
from todo import app, db
from todo.forms import RegistrationForm, LoginForm, EditProfileForm, AddTaskForm, UpdateCompletedTask
from todo.models import User, TaskList
from flask_login import login_user, current_user, login_required, logout_user
from werkzeug.urls import url_parse
from datetime import datetime


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/')
def index():
    return render_template('index.html', title='home')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user')
        return redirect(url_for('index'))
    return render_template('registration.html', title='register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            return redirect(url_for('index'))
        return redirect(next_page)
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/mytask', methods=['POST', 'GET'])
@login_required
def my_task():
    form_add_task = AddTaskForm()
    form_update_task = UpdateCompletedTask()
    if form_add_task.validate_on_submit():
        task = TaskList(task_name=form_add_task.task_name.data, doer=current_user)
        db.session.add(task)
        db.session.commit()
    user = User.query.filter_by(username=current_user.username).first()
    task_list = user.tasks.filter_by(task_status=0)

    if form_update_task.validate_on_submit():
        if form_update_task.task_status.data is True:
            task=TaskList(task_status=1, doer=current_user)
            db.session.add(task)
            db.session.commit()

    return render_template('my_task.html', title='my tasks',
                           form_add_task=form_add_task,
                           form_update_task=form_update_task,
                           task_list=task_list,
                           user=user
                           )


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('edit_profile.html', form=form, title='edit profile')
