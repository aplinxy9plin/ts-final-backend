import re
import uuid
import hashlib
from json.decoder import JSONDecodeError

from psycopg2 import sql
from flask import Blueprint, request, jsonify

from app.postgres import Database
from app.models import User, authorize
from personal_area.registration import hash_password

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth', methods=['POST'])
def authorization():
    user_data = request.get_json(silent=True)
    if not user_data:
        return jsonify(text="JSON не найден"), 204
    
    login = user_data.get("login")
    password = user_data.get("password")

    database = None
    try:
        database = Database()
        
        user_data = database.login(login)
        if type(user_data) == str:
            return jsonify({"messageError": user_data}), 500
    
        if user_data:
            if check_password(user_data, password):
                if user_data["status_active"] == True:
                    print(user_data)
                    user = User(
                        id=user_data["id"],
                        username=user_data["username"],
                        role=user_data["role"]
                    )
                    authorize[user.get_token()] = user

                    database.insert_data("UPDATE users SET last_login=now() \
                                        WHERE username='{username}'".format(
                        username=user.get_username()
                    ))
                    return jsonify({"UserToken": user.get_token(), "role": user.get_role()})
                return jsonify({'message': 'Пользователь заблокирован'}), 401
        return jsonify({'message': 'Неправильный логин или пароль'}), 401

    # except TypeError:
    #     return jsonify({"messageError": "Нет подключения к БД"}), 500
    finally:
        database.close()
    
    return jsonify(True)


def check_password(user_data, user_pass):
    new_pass = hash_password(user_pass, user_data['salt'])

    return user_data['password'].tobytes() == new_pass
