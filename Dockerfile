FROM docker pull ghcr.io/fjelltopp/fjelltopp-base-images/python-fjelltopp-base:master

COPY ./ /var/www/navigator_api
WORKDIR /var/www/navigator_api
RUN mkdir .venv && pipenv sync

EXPOSE 5003
