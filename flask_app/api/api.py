import hashlib

from flask import Blueprint, jsonify, request
from psycopg2 import sql

from app.postgres import Database
from app.models import check_auth, authorize

api_bp = Blueprint('api', __name__)


@api_bp.route('/documents', methods=['GET', "POST"])
def documets():
    user = check_auth(request.headers, __name__)
    if user != True:
        return user
    user = authorize.get(request.headers.get('UserToken'))
    try:
        database = Database()
    except TypeError:
        return jsonify({"message": "Нет подключения к БД"})
    
    result = {}

    database.close()
    return jsonify(result)
