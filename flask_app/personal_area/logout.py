from flask import Blueprint, request, jsonify

from app.models import authorize, check_auth

logout_bp = Blueprint('logout', __name__)


@logout_bp.route('/logout', methods=['GET'])
def logout():
    """Logout Page"""

    user = check_auth(request.headers, __name__)
    if user != True:
        return user
    user = authorize.get(request.headers.get('UserToken'))

    authorize.pop(user.get_token())
    return jsonify({'message': 'Пользователь вышел'}), 401, {'ContentType': 'application/json'}
