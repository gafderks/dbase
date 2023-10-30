#############
## BUILDER ##
#############
FROM python:3.11-slim as base

RUN mkdir -p /app
WORKDIR /app

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

#############
## RUNTIME ##
#############

FROM python:3.11-slim as runtime

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
RUN mkdir ${APP_HOME}/media
WORKDIR ${APP_HOME}

COPY --chown=appuser:appuser ./entrypoint.sh .
RUN sed -i 's/\r$//g'  ./entrypoint.sh && \
    chmod +x ./entrypoint.sh

COPY --from=base ${APP_HOME}/static ./static
COPY --from=base ${APP_HOME}/.venv ./.venv
COPY . .

RUN chown -R appuser:appuser ${APP_HOME}

USER 999

ENV PATH="/${APP_HOME}/.venv/bin:$PATH"

RUN django-admin compilemessages

ENTRYPOINT [ "./entrypoint.sh" ]

# Migrate (separate command, do not want to run this simultaneously if started multiple times.)

# TODO: https://snyk.io/blog/best-practices-containerizing-python-docker/#:~:text=5.%20Handle%20unhealthy%20states%20of%20your%20containerized%20Python%20application
