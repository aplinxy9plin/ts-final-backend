from app.errorhandler import error_bp

from api.api import api_bp

from vacancy.create_new_vacancy import create_new_vacancy_bp
from vacancy.get_vacancy import get_vacancy_bp

from personal_area.logout import logout_bp
from personal_area.authorization import auth_bp
from personal_area.registration import registration_bp


def route(app):
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(registration_bp)
    app.register_blueprint(logout_bp)
    app.register_blueprint(create_new_vacancy_bp)
    app.register_blueprint(get_vacancy_bp)
    app.register_blueprint(error_bp)

    return True


def csrf_exempt(csrf):
    csrf.exempt(api_bp)
    csrf.exempt(auth_bp)
    csrf.exempt(registration_bp)
    csrf.exempt(logout_bp)
    csrf.exempt(create_new_vacancy_bp)
    csrf.exempt(get_vacancy_bp)

    return True
