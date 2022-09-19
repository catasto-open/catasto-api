# https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker
# adapted to poetry

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

# Install packages and dependencies
RUN apt-get update \
    && apt-get install gcc git curl -y \
    && apt-get clean

# Install Poetry
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false

# Copy using poetry.lock* in case it doesn't exist yet
COPY ./pyproject.toml ./poetry.lock* /app/

# install dependencies
RUN poetry install --no-root --no-dev

# copy project
COPY ./ /app

# expose port
EXPOSE 5000
