# Pour utiliser Flask, rediriger vers une autre route et afficher un template
from flask import Flask, abort
# Pour connecter à la BDD
from flask_sqlalchemy import SQLAlchemy
# gestion des paramètres de l'utilisateur connecté
from flask_login import LoginManager, current_user
from flask_bootstrap import Bootstrap
# gestion des utilisateurs
from flask_admin import Admin
from flask_mail import Mail, Message
from functools import wraps

application = Flask(__name__)

application.config.from_pyfile('config.py')

Bootstrap(application)
db = SQLAlchemy(application)
admin = Admin(application, 'Gestion des utilisateurs', base_template='users/users.html')
login = LoginManager(application)
login.init_app(application)
mail = Mail(application)

from app.models.userModels import Account


@application.route('/')
def home_page():
    return 'home start'


@login.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))


from app.routes.users import users_app
from app.routes.scan import scan_app

application.register_blueprint(users_app)
#application.register_blueprint(translation_app)
application.register_blueprint(scan_app)

from app.template_filter.ValueStatus import value_status_file

if __name__ == "__main__":
    application.run()
