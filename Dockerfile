FROM python:3.11.4-bullseye
LABEL maintainers="<PLACE_HOLDER> <<PLACE_HOLDER_EMAIL>>"

WORKDIR /usr/src

# build args
ARG POETRY_VERSION=1.4.2

# install poetry
USER 1001
ENV POETRY_VENV_PATH=/usr/src/.poetry \
    POETRY_VERSION=${POETRY_VERSION} \
    POETRY_HOME=/usr/src/.poetry \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_CACHE_DIR=/usr/src/.cache/pypoetry


ENV PATH="${POETRY_HOME}/bin:${PATH}"

RUN python -m venv ${POETRY_VENV_PATH} \
    && ${POETRY_VENV_PATH}/bin/pip install -U pip setuptools \
    && ${POETRY_VENV_PATH}/bin/pip install poetry==${POETRY_VERSION}

RUN mkdir -p ${POETRY_CACHE_DIR} \
    && chmod 775 -R ${POETRY_HOME} \
    && chown 1001:0 -R ${POETRY_HOME}

# run your python project within poetry shell
ENTRYPOINT [ "/usr/src/.poetry/bin/poetry", "run" ]

# copy project dependencies
COPY *.toml *.lock ./

# modify the pyproject to reference to different JFrog registery depending on env
# install the dependencies
RUN set -x \
    && poetry install --no-dev --no-root \
    && poetry cache clear pypi --all -n \
    && rm -rf ${POETRY_CACHE_DIR}/*

# copy project src
COPY transcripts transcripts