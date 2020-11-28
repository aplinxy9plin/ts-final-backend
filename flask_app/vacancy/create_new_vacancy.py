from flask import Blueprint, jsonify, request
from psycopg2 import sql

from app.postgres import Database
from app.models import check_auth, authorize

create_new_vacancy_bp = Blueprint('create_new_vacancy', __name__)

@create_new_vacancy_bp.route('/create_new_vacancy', methods=["POST"])
def create_new_vacancy():
    user = check_auth(request.headers, __name__)
    if user != True:
        return user
    user = authorize.get(request.headers.get('UserToken'))
    try:
        database = Database()
    except TypeError:
        return jsonify({"messageError": "Нет подключения к БД"})
    
    vacancy_data = request.get_json(silent=True)
    if not vacancy_data:
        return jsonify(text="JSON не найден"), 204

    directories = [
        (["title"], "skills"),
        (["title"], "work_address"),
        (["title"], "type_employment"),
        (["title"], "professional_area"),
        (["title", "description"], "grade"),
        (["title", "description"], "working_conditions"),
        (["title", "description"], "job_responsibilities"),
        (["title", "description"], "special_advantages"),
        (["title", "description", "professional_area_id"], "specializations")

    ]

    check = check_fields(directories, vacancy_data)
    if type(check) == list:
        return "В json отсутсвуют поля: {}".format(",".join(i for i in check))

    values = {}

    for fields, table in directories:
        for value in vacancy_data[table]:
            if not values.get(table): 
                values[table] = []
            if type(value) == int:
                values[table].append(value)
            elif type(value) == list:
                if table == "specializations":
                    value.append(values["professional_area"][0])
                id = insert_new_data_in_directory(database, fields, value, table)
                if type(id) == int:
                    values[table].append(id)
            elif type(value) == str:
                id = insert_new_data_in_directory(database, fields, [value], table)
                if type(id) == int:
                    values[table].append(id)

    check = insert_vacancy(database, values, user)

    database.close()
    return jsonify(True)


@create_new_vacancy_bp.route('/get_directories_for_vacancies', methods=["GET"])
def get_directories_for_vacancies():
    user = check_auth(request.headers, __name__)
    if user != True:
        return user
    user = authorize.get(request.headers.get('UserToken'))
    try:
        database = Database()
    except TypeError:
        return jsonify({"messageError": "Нет подключения к БД"})
    
    result = {
        "professional_area": {}
    }

    directories = [
        (["id", "title"], "skills"),
        (["id", "title"], "work_address"),
        (["id", "title"], "type_employment"),
        (["id", "title", "description"], "grade"),
        (["id", "title", "description"], "working_conditions"),
        (["id", "title", "description"], "job_responsibilities"),
        (["id", "title", "description"], "special_advantages")
    ]

    for fields, table in directories:
        result[table] = select_info(database, fields, table)

    res = database.select_data("""
        SELECT 
            s.id,
            s.title,
            s.description,
            pa.id,
            pa.title
        FROM specializations s
        LEFT JOIN professional_area pa on pa.id = s.professional_area_id
    """)
    
    for id, title, description, pa_id, pa_title in res:
        if not result["professional_area"].get(pa_title): 
            result["professional_area"][pa_title] = {
                "specializations": [],
                "title": pa_title,
                "id": pa_id
            }
        
        result["professional_area"][pa_title]["specializations"].append({
            "id": id,
            "title": title,
            "description": description
        })

    database.close()
    return jsonify(result)


def select_info(database, fields, table):
    """
    Example:
        fields = ['', '']
        table = ''
    """
    res = database.select_data(sql.SQL("SELECT {fields} FROM {table}").format(
        fields=sql.SQL(",").join(sql.Identifier(i) for i in fields),
        table=sql.Identifier("public", table)
    ))

    return res


def check_fields(directories, vacancy_data):
    valid = []
    for dir_ in directories:
        if not vacancy_data.get(dir_[1]):
            valid.append(dir_[1])

    return valid if valid else True


def insert_new_data_in_directory(database, fields, values, table):
    """
    Example:
        fields = ['', '']
        values = []
        table = ''
    
    Returned: id
    """
    res = database.insert_data(sql.SQL("INSERT INTO {table}({fields}) VALUES({values})").format(
        fields=sql.SQL(",").join(sql.Identifier(i) for i in fields),
        table=sql.Identifier("public", table),
        values=sql.SQL(",").join(sql.Literal(i) for i in values)
    ))

    return database.select_data(sql.SQL("SELECT id FROM {table} WHERE {conditions};").format(
        table=sql.Identifier("public", table),
        conditions=sql.SQL("{field}={value}").format(
            field=sql.Identifier(fields[0]),
            value=sql.Literal(values[0])
        )))[0][0]


def insert_vacancy(database, values, user):
    fields = [
        "specializations",
        "grade",
        "work_address"
    ]

    id = database.select_data(sql.SQL("INSERT INTO vacancy({fields}, create_user_id, create_date) VALUES({values}, {user_id}, now()) RETURNING id").format(
        fields=sql.SQL(",").join(sql.Identifier(f'{i}_id') for i in fields),
        values=sql.SQL(",").join(sql.Literal(values[i][0]) for i in fields),
        user_id=sql.Literal(user.get_id())
    ))

    fields = [
        ("skill_id", "skills", "skills_for_a_vacancy"),
        ("type_employment_id", "type_employment", "type_employment_for_a_vacancy"),
        ("working_condition_id", "working_conditions", "working_condition_for_a_vacancy"),
        ("job_responsibilities_id", "job_responsibilities", "job_responsibilities_for_a_vacancy"),
        ("special_advantage_id", "special_advantages", "special_advantage_for_a_vacancy")
    ]

    transaction = []

    for field, row, table in fields:
        for val in values[row]:
            transaction.append(sql.SQL("INSERT INTO {table}({fields}, vacancy_id) VALUES({values}, {id});").format(
                table=sql.Identifier("public", table),
                fields=sql.Identifier(field),
                values=sql.Literal(val),
                id=sql.Literal(id[0][0])
            ))

    return database.insert_data(sql.SQL("""BEGIN; 
                {}
                COMMIT;""").format(sql.SQL(' ').join(i for i in transaction)))
