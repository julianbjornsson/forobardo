from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_mail import Mail
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'b0f1d41b685a2748b30c4913528d2f56'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Necesitas una cuenta para acceder a esta caracteristica.'
migrate = Migrate(app, db)
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'rollinga1983@gmail.com'
app.config['MAIL_PASSWORD'] = 'comandante1'
mail = Mail(app)

from flaskblog import routes
from flaskblog.models import User, Post, Comment
admin = Admin(app, name='Forobardo (Admin)', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(Comment, db.session))
