FROM python:3.11-slim as base

RUN mkdir -p /app
WORKDIR /app

RUN apt-get update
RUN apt-get -y install gettext git curl

RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - &&\
apt-get install -y nodejs

RUN npm install -g gulp-cli

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pipenv wheel
COPY ./Pipfile .
COPY ./Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

COPY ./package-lock.json .
COPY ./package.json .

RUN npm ci

COPY . .

RUN pipenv run ./manage.py compilemessages
RUN pipenv run ./manage.py collectstatic --noinput

FROM python:3.11-slim as runtime

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIPENV_VENV_IN_PROJECT=1 

RUN pip install --upgrade pipenv wheel

COPY . /app
COPY --from=base /app/static /app/static
COPY --from=base /app/.venv /app/.venv

WORKDIR /app

# Create and switch to a new user
# RUN adduser -D appuser
# WORKDIR /home/appuser
# USER appuser

EXPOSE 8000

# CMD pipenv run python /app/manage.py runserver 8000


CMD pipenv run gunicorn --bind 0.0.0.0:8000 --timeout 120 --workers 2 dbase.wsgi
