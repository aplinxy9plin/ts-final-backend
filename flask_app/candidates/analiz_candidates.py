from flask import Blueprint, jsonify, request
from psycopg2 import sql

from app.postgres import Database
from app.models import check_auth, authorize

from vacancy.create_new_vacancy import check_fields

analiz_candidates_bp = Blueprint('analiz_candidates', __name__)

@analiz_candidates_bp.route('/analiz_all_candidates', methods=["GET"])
def analiz_all_candidates():
    user = check_auth(request.headers, __name__)
    if user != True:
        return user
    user = authorize.get(request.headers.get('UserToken'))
    
    try:
        database = Database()
    except TypeError:
        return jsonify({"messageError": "Нет подключения к БД"})
    
    result = {}

    candidates = database.select_data("""
        SELECT
            c.id candidates_id,
            c.firstname candidates_firstname,
            c.lastname candidates_lastname,
            v.id vacancy_id,
            s.title specializations_title,
            sc.title status_title,
            get_score_candidate(c.id) score
        FROM candidates c
            LEFT JOIN answer_on_question_candidate aoqc on c.id = aoqc.candidate_id
            LEFT JOIN vacancy v on c.vacancy_id = v.id
            LEFT JOIN specializations s on v.specializations_id = s.id
            LEFT JOIN statuses_candidate sc on c.status_id = sc.id
    """)

    for candidat in candidates:
        candidates_id = candidat['candidates_id']
        result[candidates_id] = {}
        for key in candidat.keys():
            result[candidates_id][key] = candidat[key]
    
    result = [result[key] for key in result]

    database.close()
    return jsonify(result)