FROM python:3.9.6

RUN pip3 install uwsgi pipenv

WORKDIR /var/www/navigator_frontend

ADD Pipfile.lock /var/www/navigator_frontend/Pipfile.lock
RUN pipenv sync --dev

ADD uwsgi-app.ini /var/www/uwsgi/app.ini

CMD ["uwsgi", "/var/www/uwsgi/app.ini"]
