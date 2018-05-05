import random
import string
from functools import wraps
from flask import Blueprint, redirect, url_for, render_template, abort
from flask_login import login_user, current_user, login_required, logout_user
from flask_mail import Message
from werkzeug.security import check_password_hash, generate_password_hash
from app import db, mail
from app.models.userModels import LoginForm, User, ResetPasswordForm, SettingsForm, NewUserForm


def admin_required(f):
    '''
    check if the connected user is an admin else the access to the page is restricted
    '''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if User.query.get(current_user.get_id()).is_admin is False:
            print('No access')
            return abort(403)
        else:
            return f(*args, **kwargs)

    return decorated_function


users_app = Blueprint('users_app', __name__, template_folder='../templates/users')


@users_app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    a login form is shown, if the access is granted a specific dashboard will be shown according to the user status 
    '''
    if current_user.is_authenticated:
        return redirect(url_for('users_app.home'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.pswd, form.password.data):
                login_user(user)
                return redirect(url_for('users_app.home'))
        return render_template('login.html', error='invalid', title='Log in', form=form)
    # return 'Invalid username or password ' + generate_password_hash(form.password.data)
    return render_template('login.html', form=form, title='Log in')


@users_app.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    '''
    allows to an existing user to receive via email a new password if the user forgot the previous one
    '''
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_details_account(form, 'forget_update')
            return render_template('forgot_password.html', email='sended', title='Forgot ?', form=form)
        # return "You will receive a new password in a short moment, please check your spam folder also."
    return render_template('forgot_password.html', form=form, title='Forgot ?')


@users_app.route('/home')
@login_required
def home():
    '''
    show a homepage for the dashboard
    '''
    return render_template('dashboard_home.html', title='Home')


@users_app.route("/admin/user/add_user", methods=['GET', 'POST'])
@login_required
def add_user():
    '''
    allows to add a new user who can be an administrator or a translator
    '''
    form = NewUserForm()
    if form.validate_on_submit():
        send_details_account(form, 'new_user')
        return render_template('add_user.html', form=form, title='Add a new user', email='sended')
    # return 'New user has been created, the password has been send to his/her email '
    return render_template('add_user.html', form=form, title='Add a new user')

@users_app.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
    '''
    allows to an user to change his/her own settings
    '''
    item = User.query.get(current_user.get_id())
    user = User.query.get(item)
    form = SettingsForm(obj=item)
    if form.validate_on_submit():
        user_updated = User.query.get(current_user.get_id())
        user_updated.email = form.email.data
        if ((check_password_hash(current_user.pswd, form.pswd.data) == False) and (len(form.pswd.data) != 0) and (
                len(form.pswd.data.strip()) != 0)):
            user_updated.pswd = generate_password_hash(form.pswd.data)
        db.session.commit()
        return redirect(url_for('user.edit_view'))
    return render_template('settings.html', form=form, title='Settings')


@users_app.route('/logout')
@login_required
def logout():
    '''
	to logout from the dashboard and to be redirect to the login form
    '''
    logout_user()
    return redirect(url_for('users_app.login'))


def password_generator(size=6, chars=string.ascii_uppercase + string.digits):
    '''
    generate a password of 6 characters composed with random numbers and letters (in uppercase) 
    '''
    return ''.join(random.choice(chars) for _ in range(size))


def send_details_account(form, type):
    '''
    send the details account of a user to his or her email and according to the function where it was called the content of the email will be changed
    with a new password
    '''
    password = password_generator()
    hash_password = generate_password_hash(password)
    if type == 'new_user':
        subject = 'Account details for Maya translator website'
        new_user = User(email=form.email.data, pswd=hash_password, is_admin=form.is_admin.data)
        db.session.add(new_user)
    elif type == 'forget_update':
        subject = 'Your new password for your account on Maya translator website'
        user = User.query.filter_by(email=form.email.data).first()
        user.pswd = hash_password
    db.session.commit()
    msg = Message(subject, sender='gamaliny@gmail.com',
                  body='Your login is :' + form.email.data + ' and your password is ' + password,
                  recipients=[form.email.data])
    mail.send(msg)
