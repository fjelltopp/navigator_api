FROM fjelltopp/python-fjelltopp-base:3.9

COPY ./ /var/www/navigator_api
WORKDIR /var/www/navigator_api
RUN mkdir .venv && pipenv sync

EXPOSE 5003
