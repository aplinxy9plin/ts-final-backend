import os

from flask import Flask
from flask_cors import CORS
from flask_sslify import SSLify
from flask_wtf.csrf import CsrfProtect

from app.router import route, csrf_exempt
from app.models import User
from app.config import config, init_config


def create_flask_app():
    app = Flask(__name__)
    csrf = CsrfProtect(app)
    # sslify = SSLify(app)
    CORS(app)
    
    route(app)
    csrf_exempt(csrf)

    path = os.environ.get('CONFIG_PATH') if os.environ.get(
        'CONFIG_PATH') != None else "/home/user2020/backend_hack/backend_final/flask_app/settings.ini"
    init_config(path)
    try:
        #   Flask application configuration
        app.config.update(dict(
            SECRET_KEY=str(config['FLASK_APP']['FLASK_APP_SECRET_KEY']),
            WTF_CSRF_SECRET_KEY=str(
                config['FLASK_APP']['FLASK_APP_WTF_CSRF_SECRET_KEY']),
        ))
        print(f"\n\033[32m Сервер запустился с конфигом:\n\033[32m {path}\n")
    except KeyError:
        print(f"\033[31m Файл {path} не найден или неверный")
        shutdown_server()

    return app


def shutdown_server():
    import subprocess
    import signal

    print('\033[31m Server shutting down...')
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()

    for line in out.splitlines():
        if b'flask' in line or b'python' in line:
            pid = int(line.split(None, 1)[0])
            os.kill(pid, signal.SIGKILL)
