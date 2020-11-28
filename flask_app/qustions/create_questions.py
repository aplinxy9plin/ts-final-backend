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


@create_questions_bp.route('/create_questions', methods=["POST"])
def create_questions():
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
        (["title", "description"], "grade"),
        (["title", "description"], "question_types"),
        (None, "title"),
        (None, "question"),
        (None, "answers_on_question")        
    ]

    check = check_fields(directories, vacancy_data)
    if type(check) == list:
        return "В json отсутсвуют поля: {}".format(",".join(i for i in check))

    values = {}

    for fields, table in directories:
        values[table] = []
        if table in ["title", "question", "skills", "grade", "question_types"]:
            values[table] = vacancy_data[table]
        elif table == 'answers_on_question':
            for value in vacancy_data[table]:
                values[table].append(value)

    question_id = insert_questions(database, values)
    check = insert_answers(database, question_id, values['answers_on_question'])

    database.close()
    return jsonify(check)


def insert_questions(database, values):
    """
    values = {
        'skills': <int>,
        'grade': <int>,
        'question_types': <int>,
        'title': <str>,
        'question': <str>
    }
    Returned: id
    """
    fields = [
        ("question_types", "question_type_id"),
        ("grade", "grade_id"),
        ("skills", "skill_id"),
        ("question", "question"),
        ("title", "title")
    ]

    id = database.select_data(sql.SQL("INSERT INTO questons({fields}) VALUES({values}) RETURNING id").format(
        fields=sql.SQL(",").join(sql.Identifier(i[1]) for i in fields),
        values=sql.SQL(",").join(sql.Literal(values[i[0]]) for i in fields)
    ))

    return id[0][0] if id else id


def insert_answers(database, question_id, answers):
    """
    answers = [
        {
            "answer": "foobar",
            "is_true ": false
        }
    ]
    Returned: True
    """
    fields = [
        "answer",
        "is_true"
    ]

    transaction = []
    
    for answer in answers:
        transaction.append(sql.SQL("INSERT INTO answers_on_question({fields}, question_id) VALUES({values}, {question_id});").format(
                table=sql.Identifier("public", "answers_on_question"),
                fields=sql.SQL(",").join(sql.Identifier(i) for i in fields),
                values=sql.SQL(",").join(sql.Literal(answer[i]) for i in fields),
                question_id=sql.Literal(question_id)
            ))

    return database.insert_data(sql.SQL("""BEGIN; 
                {}
                COMMIT;""").format(sql.SQL(' ').join(i for i in transaction)))