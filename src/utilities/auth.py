from flask_login import LoginManager
from models.user import User
from db.database import db

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
