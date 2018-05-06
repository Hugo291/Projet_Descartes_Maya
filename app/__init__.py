from flask import Flask, abort, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_bootstrap import Bootstrap
from flask_admin import Admin
from flask_mail import Mail, Message
from functools import wraps

from werkzeug.security import generate_password_hash

application = Flask(__name__)

application.config.from_pyfile('config.py')

Bootstrap(application)
db = SQLAlchemy(application)
admin = Admin(application, 'Gestion des utilisateurs', base_template='users/users.html')
login = LoginManager(application)
login.init_app(application)
mail = Mail(application)

from app.models.userModels import User
import app.models.DataBase


# print('Start drop')
# db.drop_all()
# print('Start Create')
db.create_all()

@application.route('/')
def home_page():
    return render_template('home.html')


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@application.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


from app.routes.users import users_app
from app.routes.scan import scan_app
from app.routes.translation import translation_app

application.register_blueprint(users_app)
application.register_blueprint(translation_app)
application.register_blueprint(scan_app)

from app.template_filter.ValueStatus import value_status_file


if __name__ == "__main__":
    application.run()
