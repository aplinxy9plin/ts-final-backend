import time
import datetime

from flask import Blueprint, jsonify, request
from psycopg2 import sql

from app.postgres import Database
from app.models import check_auth, authorize

get_vacancy_bp = Blueprint('get_vacancy', __name__)

@get_vacancy_bp.route('/get_all_vacancy', methods=["GET"])
def get_all_vacancy():
    user = check_auth(request.headers, __name__)
    if user == True:
        user = authorize.get(request.headers.get('UserToken'))
    
    try:
        database = Database()
    except TypeError:
        return jsonify({"messageError": "Нет подключения к БД"})
    
    status_id = [2]
    fields = [
        ("v", "id"),
        ("v", "create_date"),
        ("sp", "title"),
        ("pa", "title"),
        ("sv", "title")
    ] 
    if type(user) != tuple:
        if user.get_role() == 1:
            status_id = [1, 2, 3]
    result = []
    res = database.select_data(sql.SQL("""
        SELECT 
            {fields}    
        FROM vacancy v
            LEFT JOIN specializations sp on sp.id = v.specializations_id
            LEFT JOIN professional_area pa on pa.id = sp.professional_area_id
            LEFT JOIN statuses_vacancy sv on sv.id = v.status_id
        WHERE
            status_id in ({status_id})
    """).format(
        fields=sql.SQL(",").join(sql.Identifier(i[0], i[1]) for i in fields),
        status_id=sql.SQL(",").join(sql.Literal(i) for i in status_id)))
    if res:
        for id, dt, specialization, professional_area, status in res:
            result.append({
                "id": id,
                "dt": time.mktime(datetime.datetime.strptime(dt.strftime("%d/%m/%Y"), 
                                             "%d/%m/%Y").timetuple()),
                "specialization": specialization,
                "professional_area": professional_area
            })
            if type(user) != tuple:
                if user.get_role() == 1:
                    result[-1]['status'] = status
    database.close()
    return jsonify(result)


@get_vacancy_bp.route('/get_vacancy/<int:vacancy_id>', methods=["GET"])
def get_vacancy(vacancy_id):
    try:
        database = Database()
    except TypeError:
        return jsonify({"messageError": "Нет подключения к БД"})
    
    result = {
        "specialization": {},
        "grade": {}
    }
    res = database.select_data(sql.SQL("""
        SELECT 
            v.create_date dt,
            sp.title specialization_title,
            sp.description specialization_description,
            g.title grade_title,
            g.description grade_description,
            wa.title work_address,
            pa.title professional_area
        FROM vacancy v
            LEFT JOIN specializations sp on sp.id = v.specializations_id
            LEFT JOIN grade g on g.id = v.grade_id
            LEFT JOIN work_address wa on wa.id = v.work_address_id
            LEFT JOIN professional_area pa on pa.id = sp.professional_area_id
        WHERE 
            v.id in ({})
    """).format(sql.Literal(vacancy_id)))
    if res:
        for row in res:
            for key in row.keys():
                if key.split("_")[-1] in ["title", "description"]:
                    result["_".join(i for i in (key.split("_")[:-1]))][key.split("_")[-1]] = row[key]
                elif not key == 'dt':
                    result[key] = row[key]
                else:
                    result[key] = time.mktime(datetime.datetime.strptime(row[key].strftime("%d/%m/%Y"), 
                                             "%d/%m/%Y").timetuple())
    else:
        return jsonify({"message": "Вакансия не найдена"}), 404

    params_data = [
        {
            "fields": ["title"],
            "table": "skills_for_a_vacancy",
            "module_table": "skills",
            "module": "skill_id"
        },
        {
            "fields": ["title"],
            "table": "type_employment_for_a_vacancy",
            "module_table": "type_employment",
            "module": "type_employment_id"
        },
        {
            "fields": ["title"],
            "table": "soft_requirement_for_a_vacancy",
            "module_table": "soft_requirements",
            "module": "soft_requirement_id"
        },
        {
            "fields": ["title"],
            "table": "technologies_and_tools_for_a_vacancy",
            "module_table": "technologies_and_tools",
            "module": "technologies_and_tools_id"
        },
        {
            "fields": ["title", "description"],
            "table": "working_condition_for_a_vacancy",
            "module_table": "working_conditions",
            "module": "working_condition_id"
        },
        {
            "fields": ["title", "description"],
            "table": "job_responsibilities_for_a_vacancy",
            "module_table": "job_responsibilities",
            "module": "job_responsibilities_id"
        },
        {
            "fields": ["title", "description"],
            "table": "special_advantage_for_a_vacancy",
            "module_table": "special_advantages",
            "module": "special_advantage_id"
        }
    ]

    for param in params_data:
        result[param['module_table']] = []
        res = get_data_from_directory(database, param, vacancy_id)

        for row in res:
            if len(param['fields']) == 1: 
                result[param['module_table']].append(row[0])
            else:
                module = {}
                for key in row.keys():
                    module[key] = row[key]
                result[param['module_table']].append(module)
                
        
    database.close()
    return jsonify(result)


def get_data_from_directory(database, params, vacancy_id):
    return database.select_data(sql.SQL("""
        SELECT 
            {fields}
        FROM {table} table_
            LEFT JOIN {module_table} module on module.id=table_.{module}
        WHERE
            vacancy_id={vacancy_id};
    """).format(
        fields=sql.SQL(",").join(sql.Identifier(i) for i in params["fields"]),
        table=sql.Identifier("public", params["table"]),
        module_table=sql.Identifier("public", params["module_table"]),
        module=sql.Identifier(params["module"]),
        vacancy_id=sql.Literal(vacancy_id)
    ))