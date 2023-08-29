FROM python:3.9

# Install packages and dependencies
RUN apt-get update \
    && apt-get install gcc git curl libxrender1 -y \
    && apt-get clean

# Install wkhtmltopdf
COPY /wkhtmltopdf/wkhtmltox/bin/ /usr/bin/

# Install Poetry
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false

# Copy using poetry.lock* in case it doesn't exist yet
COPY ./pyproject.toml ./poetry.lock* /app/
WORKDIR /app

# install dependencies
RUN poetry install --no-root --only main

# copy project
COPY ./ /app

# run the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
