from flask import jsonify, Blueprint
from flask_wtf.csrf import CSRFError

error_bp = Blueprint('error', __name__)


@error_bp.errorhandler(CSRFError)
def handle_csrf_error(e):
    return jsonify({'message': 'Не верный токен'}), 401, {'ContentType': 'application/json'}
