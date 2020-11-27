import re
import uuid
import hashlib
from json.decoder import JSONDecodeError

from psycopg2 import sql
import difflib
from flask import Blueprint, request, jsonify

from app.postgres import Database

registration_bp = Blueprint('registration', __name__)

@registration_bp.route('/get_roles', methods=['GET'])
def get_roles():
    return jsonify({
        "1": "HR",
        "2": "Employee",
        "3": "Candidate"
    })

@registration_bp.route('/registration', methods=['POST'])
def registration():
    user_data = request.get_json(silent=True)
    if not user_data:
        return jsonify(text="JSON не найден"), 204

    database = None
    try:
        database = Database()

        valid = valid_user_data(database, user_data)
        if valid != True:
            return jsonify(valid), 400

        salt = uuid.uuid4().hex
        user_data['password'] = hash_password(user_data['password'], salt)

        valid = add_to_database(database, user_data)        
        if valid != True:
            return jsonify(valid), 500

        user_data["uuid"] = get_user_id(database, user_data['email'])[0][0]
        valid = insert_salt_for_user(database, user_data["uuid"], salt)
        if valid != True:
            return jsonify(valid), 500
        

    except TypeError:
        return jsonify({"messageError": "Нет подключения к БД"}), 500
    finally:
        database.close()

    return jsonify("Пользователь успешно зарегестрирован")


def valid_user_data(database, user_data):
    """Checking user data"""
    vozvrat = []

    valid = valid_password(user_data.get('password'), user_data.get('confirm_password'))
    if valid != True:
        vozvrat.append({"field": "password", "message": valid})

    valid = valid_email(database, user_data.get('email'), user_data.get('password'))
    if valid != True:
        vozvrat.append({"field": "email", "message": valid})

    return True if len(vozvrat) == 0 else vozvrat


def valid_email(database, email, password):
    """Valid email"""
    if email == None:
        return "email не введён"
    if re.search("""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""", email) == None:
        return "email не удовлетворяет требованиям"
    if email == password or similarity(email, password) > 0.4:
        return "email повторяется с паролем"
    if bool(get_user_id(database, email)):
        return "Пользователь с таким email уже зарегестрирован"
    return True


def get_user_id(database, email):
    return database.select_data(sql.SQL("SELECT id FROM users WHERE email={}").format(sql.Literal(email)))


def valid_password(password, confirm_password):
    """Valid password"""
    VALID_CHARS = [
        "[A-Z]{1,70}",
        "[a-z]{1,70}",
        "[0-9]{1,70}",
        "[\!\@\#\$\%\^\&\*\(\)\_\-\+\:\;\,\.]{0,70}"
    ]
    if password != confirm_password:
        return "Пароли не совпадают"
    if password == None:
        return "Пароль не введён"
    if len(password) < 6:
        return "Пароль не удовлетворяет требованиям"

    for val in VALID_CHARS:
        if re.search(
                val, password) == None:
            return "Пароль не удовлетворяет требованиям"

    # Проверка на 3 подряд идущие одинаковые символы
    last_char = ""
    quantity = 0
    for char in password:       
        if char != last_char:
            last_char = char
        elif char == last_char and quantity < 1:
            quantity += 1
        else:
            return "Пароль не удовлетворяет требованиям"
    return True


def similarity(s1, s2):
    """Affinity check"""
    normalized1 = s1.lower()
    normalized2 = s2.lower()
    matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
    return matcher.ratio()


def add_to_database(database, user_data):
    query = "INSERT INTO users(id, email, password, username, role) VALUES({id}, {email}, {password}, {username}, {role})"

    values = {
        "id": sql.Literal(str(uuid.uuid4())),
        "email": sql.Literal(user_data['email']),
        "password": sql.Literal(user_data['password']),
        "username": sql.Literal(re.split(r'\@', user_data['email'])[0]),
        "role": sql.Literal(user_data['role'])
    }

    return database.insert_data(sql.SQL(query).format(**values))


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)


def insert_salt_for_user(database, user_uuid, salt):
    query = "INSERT INTO users_salt(user_id, salt) VALUES({user_id}, {salt})"

    values = {
        "user_id": sql.Literal(user_uuid),
        "salt": sql.Literal(salt)
    }

    return database.insert_data(sql.SQL(query).format(**values))
