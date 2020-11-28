from flask import Blueprint, jsonify, request
from psycopg2 import sql

from app.postgres import Database
from app.models import check_auth, authorize

from vacancy.create_new_vacancy import select_info, check_fields

testing_bp = Blueprint('testing', __name__)

@testing_bp.route('/get_questions_for_teseting/<int:vacancy_id>', methods=["GET"])
def get_questions_for_teseting(vacancy_id):
    try:
        database = Database()
    except TypeError:
        return jsonify({"messageError": "Нет подключения к БД"})
    
    result = {}

    questons = database.select_data(sql.SQL("""
        SELECT
            q.id questons_id,
            qt.title question_type_title,
            qt.description question_type_description,
            g.title grade_title,
            s.title skills_title,
            q.title questons_title,
            q.question questons_question,
            aoq.id answer_id,
            aoq.answer answer_text
        FROM questons q
            LEFT JOIN grade g on q.grade_id = g.id
            LEFT JOIN skills s on q.skill_id = s.id
            LEFT JOIN question_types qt on q.question_type_id = qt.id
            LEFT JOIN answers_on_question aoq on q.id = aoq.question_id
        WHERE
            s.id in (SELECT skill_id FROM vacancy v WHERE v.id={vacancy_id});
    """).format(vacancy_id=sql.Literal(vacancy_id)))

    for quest in questons:
        if result.get(quest['questons_id']):
            result[quest['questons_id']]['answers'].append((quest['answer_id'], quest['answer_text']))
        else:
            res = {
            "answers": [] 
            }
            for key in quest.keys():
                if not key.split('_')[0] == 'answer':   
                    res[key] = quest[key]
            
            res["answers"].append((quest['answer_id'], quest['answer_text']))
            result[res['questons_id']] = res
        if len(result) == 3:
            break

    database.close()
    return jsonify(result)
