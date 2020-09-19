FROM pypy:3.6-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV APP_DIR /app

WORKDIR ${APP_DIR}

COPY Pipfile Pipfile.lock ${APP_DIR}/

RUN pip install pipenv --no-cache-dir && \
    pipenv install --system --deploy && \
    pip uninstall -y pipenv virtualenv-clone virtualenv && \
    mkdir ${APP_DIR}/logs && \
    mkdir /srv/origin

COPY . ${APP_DIR}/

ENV DROPBOX_BACKUP_ACCESS_TOKEN ""
ENV DROPBOX_BACKUP_WRITE_MODE "overwrite"
ENV DROPBOX_BACKUP_FROM /srv/origin
ENV DROPBOX_BACKUP_TO /backup
ENV DROPBOX_BACKUP_DEBUG_MODE false
ENV DROPBOX_BACKUP_TEST_MODE false
ENV DROPBOX_BACKUP_LOG_FOR_HUMAN false

CMD ["pypy3", "-c", "from dropbox_backup import app; app.execute();"]