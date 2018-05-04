from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length, Optional
from app import admin , db

class User(db.Model, UserMixin):
    '''
    where db.Model connect to the database throught ORM to create an "Account" class
    which refers to the same name table
    '''
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), unique=True)
    pswd = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean)


class AccountForm(ModelView):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    isAdmin = BooleanField('Administrator')
    #new_password = BooleanField('Send a new password')


class AccountSettings(ModelView):
    '''
    is used to show the list of the users account and to edit one of them, 
    it's using the plugin Flask-Admin to manage easily users account
    The removing option is using by default so there is no use to cal it here
    '''
    #list_template = 'admin/list.html'
    edit_template = 'edit_user.html'
    column_exclude_list = ['pswd']
    form_columns = ['email', 'is_admin']

def is_accessible(self):

	if not current_user.is_active or not current_user.is_authenticated:
		return False
	if Account.query.get(current_user.get_id()).is_admin is True:
		return True
	return False

class SettingsForm(FlaskForm):
    '''
    is used for the settings form
    '''
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    pswd = PasswordField('password', validators=[Optional(), Length(min=2, max=20)])


class LoginForm(FlaskForm):
    '''
    is used for the login form
    '''
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=2, max=20)])
    #remember = BooleanField('remember me') 


class NewUserForm(FlaskForm):
    '''
    is used to create a new user
    '''
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    is_admin = BooleanField('Administrator')


class ResetPasswordForm(FlaskForm):
    '''
    when a password is forgotten, it will send an email to the corresponding mail adress a new password
    '''
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])

admin.add_view(AccountSettings(User, db.session))
