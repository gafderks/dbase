#############
## BUILDER ##
#############
FROM python:3.11-slim as base
LABEL maintainer="Geert Derks <geertderks12@gmail.com>"

ENV APP_HOME=/app

RUN mkdir -p ${APP_HOME}
WORKDIR ${APP_HOME}

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl ca-certificates gnupg git

# Install Node.js
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    NODE_MAJOR=20; echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && apt-get install -y --no-install-recommends nodejs

RUN npm install -g gulp-cli@2.3.0

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DOCKER_BUILD 1

RUN pip install --upgrade --no-cache-dir pipenv==2023.10.24 wheel==0.41.2
COPY ./Pipfile .
COPY ./Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

COPY ./package-lock.json .
COPY ./package.json .

RUN npm ci && \
    npx update-browserslist-db@latest

COPY . .

RUN SECRET_KEY=dummy pipenv run ./manage.py collectstatic --noinput

###########
## NGINX ##
###########

FROM nginx:1.25.3@sha256:add4792d930c25dd2abf2ef9ea79de578097a1c175a16ab25814332fe33622de as nginx
LABEL maintainer="Geert Derks <geertderks12@gmail.com>"

COPY ./config/nginx.conf /etc/nginx/nginx.conf

RUN mkdir -p /opt/services/dbase/static
COPY --from=base /app/static /opt/services/dbase/static

#############
## RUNTIME ##
#############

FROM python:3.11-slim@sha256:f89d4d260b6a5caa6aa8e0e14b162deb76862890c91779c31f762b22e72a6cef as runtime
LABEL maintainer="Geert Derks <geertderks12@gmail.com>"

RUN apt-get update && apt-get install -y --no-install-recommends gettext

# Prevent writing pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Prevent buffering stdout and stderr
ENV PYTHONUNBUFFERED 1
ENV PIPENV_VENV_IN_PROJECT=1 

ENV APP_HOME=/app

# Create and switch to a new user
RUN groupadd -g 999 appuser && \
    useradd -r -u 999 -g appuser appuser

RUN mkdir ${APP_HOME}
RUN mkdir ${APP_HOME}/media && \
    chown appuser:appuser ${APP_HOME}/media
WORKDIR ${APP_HOME}

COPY --chown=appuser:appuser ./entrypoint.sh .
RUN sed -i 's/\r$//g'  ./entrypoint.sh && \
    chmod +x ./entrypoint.sh

COPY --from=nginx --chown=appuser:appuser /opt/services/dbase/static/staticfiles.json ./static/staticfiles.json
COPY --from=base --chown=appuser:appuser ${APP_HOME}/.venv ./.venv
COPY --chown=appuser:appuser . .

USER 999

ENV PATH="/${APP_HOME}/.venv/bin:$PATH"

RUN django-admin compilemessages

ENTRYPOINT [ "./entrypoint.sh" ]

# Migrate (separate command, do not want to run this simultaneously if started multiple times.)

# TODO: https://snyk.io/blog/best-practices-containerizing-python-docker/#:~:text=5.%20Handle%20unhealthy%20states%20of%20your%20containerized%20Python%20application
