# Use an official Python runtime as a parent image
FROM python:3.8.3

WORKDIR /flask_app

COPY requirements.txt /flask_app

RUN pip3 install --upgrade -r requirements.txt

# CMD [ "flask", "run", "--host=0.0.0.0" ]
CMD [ "/bin/sh", "-c", "gunicorn -w 1 --threads 5 -b 0.0.0.0:${VIRTUAL_PORT:-5000} 'main:create_flask_app()' --reload --timeout 180000" ]
