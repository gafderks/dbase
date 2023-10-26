FROM python:3.11-slim as base

RUN mkdir -p /app
WORKDIR /app

RUN apt-get update
RUN apt-get -y install gettext curl ca-certificates gnupg git

# Install Node.js
RUN mkdir -p /etc/apt/keyrings
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
RUN NODE_MAJOR=20; echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
RUN apt-get update && apt-get install nodejs -y

RUN npm install -g gulp-cli

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DOCKER_BUILD 1

RUN pip install --upgrade pipenv wheel
COPY ./Pipfile .
COPY ./Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

COPY ./package-lock.json .
COPY ./package.json .

RUN npm ci
RUN npx update-browserslist-db@latest

COPY . .

RUN pipenv run django-admin compilemessages
RUN SECRET_KEY=dummy pipenv run ./manage.py collectstatic --noinput

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

# TODO: DELETE NPM stuff?

EXPOSE 8000

# CMD pipenv run python /app/manage.py runserver 8000


CMD pipenv run gunicorn --bind 0.0.0.0:8000 --timeout 120 --workers 2 dbase.wsgi
