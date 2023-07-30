# python-base - environment vars
FROM python:3.11.4-bookworm as python-base

# python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# pip
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# poetry
ENV POETRY_VERSION=1.5.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

ENV PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# builder-base - dependencies and virtual env
FROM python-base as builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
       curl \
       build-essential

# install poetry
RUN curl -sSL https://install.python-poetry.org | python -

# setup with poetry
WORKDIR $PYSETUP_PATH
COPY . .
RUN poetry install --only main

# production iamge
FROM python-base as production
ENV FASTAPI_ENV=production
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY . ./app
WORKDIR /app
EXPOSE 8000
CMD ["gunicorn", "tinygen.app:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
