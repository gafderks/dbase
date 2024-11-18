#############
## BUILDER ##
#############
FROM python:3.12-slim AS base
LABEL maintainer="Geert Derks <geertderks12@gmail.com>"

ENV APP_HOME=/app

RUN mkdir -p ${APP_HOME}
WORKDIR ${APP_HOME}

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates gnupg git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    NODE_MAJOR=20; echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g gulp-cli@2.3.0

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DOCKER_BUILD=1
ENV NODE_ENV=production

RUN pip install --upgrade --no-cache-dir pipenv==2023.10.24 wheel==0.41.2
COPY ./Pipfile .
COPY ./Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

COPY ./package-lock.json .
COPY ./package.json .

RUN npm ci --omit=dev && \
    npx update-browserslist-db@latest

COPY . .

RUN SECRET_KEY=dummy pipenv run python ./manage.py collectstatic --noinput

###########
## NGINX ##
###########

FROM nginx:1.27.2@sha256:bc5eac5eafc581aeda3008b4b1f07ebba230de2f27d47767129a6a905c84f470 AS nginx
LABEL maintainer="Geert Derks <geertderks12@gmail.com>"

COPY ./config/nginx.conf /etc/nginx/nginx.conf

RUN mkdir -p /opt/services/dbase/static
COPY --from=base /app/static /opt/services/dbase/static

#############
## RUNTIME ##
#############

FROM python:3.12-slim@sha256:af4e85f1cac90dd3771e47292ea7c8a9830abfabbe4faa5c53f158854c2e819d AS runtime
LABEL maintainer="Geert Derks <geertderks12@gmail.com>"

RUN apt-get update && apt-get install -y --no-install-recommends gettext \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Prevent writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent buffering stdout and stderr
ENV PYTHONUNBUFFERED=1
ENV PIPENV_VENV_IN_PROJECT=1 

ENV APP_HOME=/app

# Create and switch to a new user
RUN groupadd -g 999 appuser && \
    useradd -r -u 999 -g appuser appuser

RUN mkdir ${APP_HOME} && \
    chown appuser:appuser ${APP_HOME}
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

ENV PATH="${APP_HOME}/.venv/bin:$PATH"

RUN django-admin compilemessages

ENTRYPOINT [ "./entrypoint.sh" ]

#############
## TESTING ##
#############

FROM base AS base-test

RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --dev

FROM runtime AS web-test

COPY --from=base-test --chown=appuser:appuser ${APP_HOME}/.venv ./.venv
