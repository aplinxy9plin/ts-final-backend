import secrets
import time

from flask import jsonify

from app.postgres import Database
from app.config import config


authorize = {}
PERMISSION_AUTHORIZATION = {
    # 0 - Admin
    # 1 - HR
    # 2 - Employee
    "logout": [0, 1, 2],
    "create_new_vacancy": [0, 2],
    "create_questions": [0, 2],
    "get_vacancy": [0, 1, 2]
}


def check_auth(headers, name):
    user = authorize.get(headers.get('UserToken'))
    if user == None:
        return jsonify({'message': 'Не верный UserToken'}), 401, {'ContentType': 'application/json'}

    allowed = user.allow(name.rsplit('.')[-1])
    if allowed != True:
        return allowed

    return True


class User ():
    def __init__(self, id, username, role):
        self.__id = id
        self.__username = username
        self.__role = role

        self.__generate_token()
        self.__time_auth = int(time.time()) + 1800

    def get_username(self):
        return self.__username

    def get_id(self):
        return self.__id

    def get_role(self):
        return self.__role

    def get_token(self):
        return self.__user_token

    def __generate_token(self):
        length = 256
        self.__user_token = secrets.token_urlsafe(length)

    def token_check(self):
        return True if (time.time() - self.__time_auth) < self.__ttl else False

    def allow(self, name_func):
        if self.__time_auth < time.time():
            authorize.pop(self.__user_token)
            return jsonify({'message': 'UserToken больше не действителен'}), 401, {'ContentType': 'application/json'}
        permission_name = PERMISSION_AUTHORIZATION.get(name_func)
        if permission_name == None:
            return jsonify({'message': 'Нет доступа'}), 403, {'ContentType': 'application/json'}
        if not self.__role in permission_name:
            return jsonify({'message': 'Нет доступа'}), 403, {'ContentType': 'application/json'}

        return True
