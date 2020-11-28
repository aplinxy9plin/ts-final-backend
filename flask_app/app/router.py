from app.errorhandler import error_bp

from vacancy.create_new_vacancy import create_new_vacancy_bp
from vacancy.get_vacancy import get_vacancy_bp
from vacancy.manage_vacancy import manage_vacancy_bp
from vacancy.manage_candidat import manage_candidat_bp
from vacancy.response_vacancy import response_vacancy_bp

from qustions.create_questions import create_questions_bp
from qustions.testing import testing_bp

from personal_area.logout import logout_bp
from personal_area.authorization import auth_bp
from personal_area.registration import registration_bp


def route(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(registration_bp)
    app.register_blueprint(logout_bp)
    app.register_blueprint(create_new_vacancy_bp)
    app.register_blueprint(get_vacancy_bp)
    app.register_blueprint(create_questions_bp)
    app.register_blueprint(testing_bp)
    app.register_blueprint(manage_vacancy_bp)
    app.register_blueprint(manage_candidat_bp)
    app.register_blueprint(response_vacancy_bp)
    app.register_blueprint(error_bp)

    return True


def csrf_exempt(csrf):
    csrf.exempt(auth_bp)
    csrf.exempt(registration_bp)
    csrf.exempt(logout_bp)
    csrf.exempt(create_new_vacancy_bp)
    csrf.exempt(get_vacancy_bp)
    csrf.exempt(create_questions_bp)
    csrf.exempt(testing_bp)
    csrf.exempt(manage_vacancy_bp)
    csrf.exempt(manage_candidat_bp)
    csrf.exempt(response_vacancy_bp)

    return True
