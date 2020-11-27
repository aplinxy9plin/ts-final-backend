from flask import Blueprint, jsonify, request
from psycopg2 import sql

from app.postgres import Database
from app.models import check_auth, authorize

create_new_vacancy_bp = Blueprint('create_new_vacancy', __name__)


@create_new_vacancy_bp.route('/get_directories_for_vacancies', methods=["GET"])
def get_directories_for_vacancies():
    # user = check_auth(request.headers, __name__)
    # if user != True:
    #     return user
    # user = authorize.get(request.headers.get('UserToken'))
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
        (["id", "title", "description"], "job_responsibilities")
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

    print(fields, values)
    return database.select_data(sql.SQL("SELECT id FROM {table} WHERE {conditions};").format(
        table=sql.Identifier("public", table),
        conditions=sql.SQL("{field}={value}").format(
            field=sql.Identifier(fields[0]),
            value=sql.Literal(values[0])
        )))[0][0]

