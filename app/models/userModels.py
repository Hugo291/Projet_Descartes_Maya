# du fichier login importer la variable db et admin
# Pour g�rer les utilisateurs
from flask_admin.contrib.sqla import ModelView
# Pour connecter � la BDD
from flask_login import UserMixin
from flask_login import current_user
# Pour le formulaire de connexion
from flask_wtf import FlaskForm
# Pour les champs du formulaire de connexion, login, pswd et se souvenir du mot de passe
from wtforms import StringField, PasswordField, BooleanField
# Pour obliger de remplir les champs ayant une certaine taille de value
from wtforms.validators import InputRequired, Email, Length, Optional

from app import admin
from app import db


class Account(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60))
    pswd = db.Column(db.String(60))
    isAdmin = db.Column(db.Boolean)


class AccountForm(ModelView):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    isAdmin = BooleanField('Administrator')
    new_password = BooleanField('Send a new password')


class AccountSettings(ModelView):
    list_template = 'admin/list.html'
    edit_template = 'edit_user.html'
    column_exclude_list = ['pswd']
    form_columns = ['email', 'isAdmin']

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if Account.query.get(current_user.get_id()).isAdmin is True:
            return True
        return False


class SettingsForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    pswd = PasswordField('password', validators=[Optional(), Length(min=2, max=20)])


class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=2, max=20)])
    remember = BooleanField('remember me')


class NewUserForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    isAdmin = BooleanField('Administrator')


class ResetPasswordForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])


# Faire trois types de vues un pour la gestion des utilisateurs
admin.add_view(AccountSettings(Account, db.session))
# Pour les param�tres
# Pour la gestion des traductions
# admin.add_view(AccountSettings(Account, db.session))
