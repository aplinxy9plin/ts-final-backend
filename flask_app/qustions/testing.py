from flask import Blueprint, jsonify, request
from psycopg2 import sql

from app.postgres import Database
from app.models import check_auth, authorize

from vacancy.create_new_vacancy import select_info, check_fields

create_questions_bp = Blueprint('create_questions', __name__)

@create_questions_bp.route('/get_directories_for_questions', methods=["GET"])
def get_directories_for_questions():
    user = check_auth(request.headers, __name__)
    if user != True:
        return user
    user = authorize.get(request.headers.get('UserToken'))
    try:
        database = Database()
    except TypeError:
        return jsonify({"messageError": "Нет подключения к БД"})
    
    result = {}

    directories = [
        (["id", "title"], "skills"),
        (["id", "title", "description"], "grade"),
        (["id", "title", "description"], "question_types")
    ]

    for fields, table in directories:
        result[table] = select_info(database, fields, table)

    database.close()
    return jsonify(result)