from flask import Blueprint, jsonify, request
from psycopg2 import sql

from app.postgres import Database
from app.models import check_auth, authorize

from vacancy.create_new_vacancy import select_info, check_fields

response_vacancy_bp = Blueprint('response_vacancy', __name__)

@response_vacancy_bp.route('/response_vacancy', methods=["POST"])
def response_vacancy():   
    try:
        database = Database()
    except TypeError:
        return jsonify({"messageError": "Нет подключения к БД"})
    
    directories = [
        (None, "firstname"),
        (None, "lastname"),
        (None, "number_phone"),
        (None, "skills"),
        (None, "technologies_and_tools"),
        (None, "vacancy_id")
    ]

    response_vacancy_data = request.get_json(silent=True)
    if not response_vacancy_data:
        return jsonify(text="JSON не найден"), 204

    check = check_fields(directories, response_vacancy_data)
    if type(check) == list:
        return "В json отсутсвуют поля: {}".format(",".join(i for i in check))

    candidate_id = insert_candidate(database, response_vacancy_data)
    check = union_candidate_and_skills(database, candidate_id, response_vacancy_data)
    if response_vacancy_data.get('answers'):
        check = write_answers(database, candidate_id, response_vacancy_data['answers'])
    database.close()
    return jsonify(check)


@response_vacancy_bp.route('/get_directories_for_response_vacancy', methods=["GET"])
def get_directories_for_response_vacancy():
    try:
        database = Database()
    except TypeError:
        return jsonify({"messageError": "Нет подключения к БД"})
    
    result = {}

    directories = [
        (["id", "title"], "skills"),
        (["id", "title"], "technologies_and_tools")
    ]

    for fields, table in directories:
        result[table] = select_info(database, fields, table)

    database.close()
    return jsonify(result)


def insert_candidate(database, response_vacancy_data):
    """
    Example:
        response_vacancy_data : {
            "firstname": "",
            "lastname": "",
            "number_phone": "",
            "link_social_network": "",
            "resume": "",
            "vacancy_id": ""
        }
    
    Returned: id
    """
    fields = [
        "firstname",
        "lastname",
        "number_phone",
        "link_social_network",
        "resume",
        "vacancy_id"
    ]
    res = database.select_data(sql.SQL("INSERT INTO {table}({fields}) VALUES({values}) RETURNING id").format(
        fields=sql.SQL(",").join(sql.Identifier(i) for i in fields),
        table=sql.Identifier("public", "candidates"),
        values=sql.SQL(",").join(sql.Literal(response_vacancy_data.get(i)) for i in fields)
    ))

    return res[0][0]


def union_candidate_and_skills(database, candidate_id, values):
    fields = [
        ("skill_id", "skills", "skills_for_a_candidate"),
        ("technologies_and_tools_id", "technologies_and_tools", "technologies_and_tools_for_a_candidate")
    ]

    transaction = []

    for field, row, table in fields:
        for val in values[row]:
            transaction.append(sql.SQL("INSERT INTO {table}({fields}, candidate_id) VALUES({values}, {candidate_id});").format(
                table=sql.Identifier("public", table),
                fields=sql.Identifier(field),
                values=sql.Literal(val),
                candidate_id=sql.Literal(candidate_id)
            ))

    return database.insert_data(sql.SQL("""BEGIN; 
                {}
                COMMIT;""").format(sql.SQL(' ').join(i for i in transaction)))


def write_answers(database, candidate_id, answers):
    transaction = []

    for question_id, answer_id in answers:
        transaction.append(sql.SQL("INSERT INTO {table}(question_id, answer_id, candidate_id, result) VALUES({question_id}, {answer_id}, {candidate_id}, (SELECT is_true FROM answers_on_question WHERE id={answer_id}));").format(
            table=sql.Identifier("public", "answer_on_question_candidate"),
            question_id=sql.Literal(question_id),
            answer_id=sql.Literal(answer_id),
            candidate_id=sql.Literal(candidate_id)
        ))

    return database.insert_data(sql.SQL("""BEGIN; 
                {}
                COMMIT;""").format(sql.SQL(' ').join(i for i in transaction)))