from flask import Blueprint, jsonify, request
from psycopg2 import sql

from app.postgres import Database
from app.models import check_auth, authorize

from vacancy.create_new_vacancy import check_fields

manage_vacancy_bp = Blueprint('manage_vacancy', __name__)


@manage_vacancy_bp.route('/get_statuses', methods=["GET"])
def get_statuses():
    user = check_auth(request.headers, __name__)
    if user != True:
        return user
    user = authorize.get(request.headers.get('UserToken'))
    
    try:
        database = Database()
    except TypeError:
        return jsonify({"messageError": "Нет подключения к БД"})
    
    result = []

    statuses = database.select_data("SELECT id, title FROM statuses_vacancy")

    for id, title in statuses:
        result.append({
            "id": id,
            "title": title
        })

    database.close()
    return jsonify(result)


@manage_vacancy_bp.route('/change_status_vacancy', methods=["POST"])
def change_status_vacancy():
    user = check_auth(request.headers, __name__)
    if user != True:
        return user
    user = authorize.get(request.headers.get('UserToken'))
    
    try:
        database = Database()
    except TypeError:
        return jsonify({"messageError": "Нет подключения к БД"})
    
    change_status_data = request.get_json(silent=True)
    if not change_status_data:
        return jsonify(text="JSON не найден"), 204
    
    directories = [
        (None, "status_id"),
        (None, "vacancy_id")
    ]

    check = check_fields(directories, change_status_data)
    if type(check) == list:
        return "В json отсутсвуют поля: {}".format(",".join(i for i in check))
    
    result = database.insert_data(sql.SQL("UPDATE vacancy SET status_id={status_id} WHERE id={vacancy_id}").format(
        status_id=sql.Literal(change_status_data['status_id']),
        vacancy_id=sql.Literal(change_status_data['vacancy_id'])
    ))
    

    database.close()
    return jsonify(result)