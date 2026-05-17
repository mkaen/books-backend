
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user, logout_user, login_user

from src.api.user.utils import compare_passwords, validate_user_registration_data, is_existing_email
from src.db.dao import db
from src.models.models import User
from src.logger.logger_config import logger
from src.api.user.service import handle_duration, get_user_data_by_email, save_data_and_fetch_user_id
from src.schemas.schemas import UserLoginSchema, UserRegisterSchema, UserPublicSchema


login_schema = UserLoginSchema()
register_schema = UserRegisterSchema()
public_schema = UserPublicSchema()


user_blueprint = Blueprint('user_api', __name__, url_prefix='/user_api')


@user_blueprint.route('/change_duration/<int:user_id>', methods=['PATCH'])
@login_required
def change_duration(user_id):
    if current_user.id != user_id:
        return jsonify({"msg": f"Current user id:{current_user.id} cannot change user id: {user_id} duration"}), 401
    data = request.json
    return handle_duration(user_id, data)


@user_blueprint.route('/current_user', methods=['GET'])
def get_current_user():
    if current_user.is_authenticated:
        return jsonify(User.get_user_dict(current_user)), 200
    return jsonify({"authenticated": False}), 401


@user_blueprint.route('/register', methods=['POST'])
def register():
    """
    Register new user to environment.

    Save new user data to db and login user.
    """
    data = register_schema.load(request.json)
    validate_user_registration_data(data)

    if is_existing_email(data.get('email').lower()):
        msg = f"User with email: {data.get('email', '')} has already registered. Registration FAILED"
        logger.info(msg)
        return jsonify({"message": msg}), 409

    user_id = save_data_and_fetch_user_id(data)
    user = db.session.get(User, user_id)

    login_user(user)
    logger.info(f"Registered new user id: {current_user.id}!")
    return jsonify({"data": public_schema.dump(user)}), 201


@user_blueprint.route('/login', methods=['POST'])
def login():
    """Validate user username and password to log user in."""
    data = login_schema.load(request.json)
    if not data:
        logger.error("Login failed! No incoming data!")
        return jsonify({"message": "Login data missing"}), 400

    email = data.get('email')
    user = get_user_data_by_email(email)

    if not user:
        logger.error(f"Fetch user data by email {email} from database failed")
        return jsonify({"message": f"Existing user with email {email} missing"}), 401

    if not compare_passwords(user.password, data.get('password')):
        return jsonify({"message": "Wrong password"}), 401

    login_user(user)
    logger.info(f"User id: {user.id} logged in")
    return jsonify(public_schema.dump(user)), 202


@user_blueprint.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout current user and redirect to home page."""
    msg = f'User id: {current_user.id} logged out'
    logout_user()
    logger.info(msg)
    return jsonify({'message': msg, 'authenticated': current_user.is_authenticated}), 200
