from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_login import LoginManager

bootstrap = Bootstrap()
mail = Mail()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hard to guess string'

    bootstrap.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    from .warehouse_management import manage as manage_blueprint
    app.register_blueprint(manage_blueprint)
    from .client_module import client as client_blueprint
    app.register_blueprint(client_blueprint)

    return app
