# Catasto API

This repository contains the source code for the catasto API, which is written in Python using the FastAPI framework. The API is designed to generate cadastral documents, such as visure, and depends on the Catasto Postgres database available [here](https://github.com/catasto-open/catasto-db/tree/develop) and on an OpenAM server.

## Requirements
- catasto-db
- OpenAM server

## Running with Docker
To run the API with Docker, you can follow these steps:

1. Clone the repository

```bash
git clone git@gitlab.com:geobeyond/catasto-api.git
```

2. Build the Docker image using the following command:

```bash
docker build . -t catasto-api --no-cache
```

3. Start the Docker container with the following command:

```bash
docker run -p 80:80 catasto-api
```

However, to make the API functional, you need to provide environment variables that point to the required services. Specifically, you need to set the following environment variables:

- ENV_STATE: Set to `dev`

- DEV_OPENAM_CLIENT_ID
- DEV_OPENAM_CLIENT_SECRET
- DEV_OPENAM_OIDC_BASE_URL
- DEV_OPENAM_OIDC_USERINFO_URL

- DEV_SISCAT_DB_SERVER_HOST
- DEV_SISCAT_DB_SERVER_PORT
- DEV_SISCAT_DB_NAME
- DEV_SISCAT_DB_USER
- DEV_SISCAT_DB_PASSWORD

These variables can be set using the -e flag when running the Docker container. For example:

```bash
docker run -p 80:80 \
-e ENV_STATE=dev \
-e DEV_OPENAM_CLIENT_ID=<client_id> \
-e DEV_OPENAM_CLIENT_SECRET=<client_secret> \
-e DEV_OPENAM_OIDC_BASE_URL=<oidc_base_url> \
-e DEV_OPENAM_OIDC_USERINFO_URL=<oidc_userinfo_url> \
-e DEV_SISCAT_DB_SERVER_HOST=<db_server_host> \
-e DEV_SISCAT_DB_SERVER_PORT=<db_server_port> \
-e DEV_SISCAT_DB_NAME=<db_name> \
-e DEV_SISCAT_DB_USER=<db_user> \
-e DEV_SISCAT_DB_PASSWORD=<db_password> \
catasto-api
```

## Running Locally

To run the API locally, you can follow these steps:

1. Create the folder /app/app on your machine and copy the folder /app/templates inside it. This will create the path /app/app/templates.

2. From the project folder, activate the [Poetry](https://python-poetry.org/) environment and start the API using the following command:

```bash
poetry shell
poetry run uvicorn app.main:app --host 0.0.0.0 --port 5000
```

The Swagger interface will be available at:

`http://localhost:5000/siscat/api/v1/docs`


## Building and Pushing the Docker Image

To build and push the Docker image, you can follow these steps:

1. Build the Docker image using the following command:

```bash
docker build . -t <your-docker-username>/catasto-api --no-cache
```

2. Push the Docker image to Docker Hub using the following command:

```bash
docker push <your-docker-username>/catasto-api
```

Note that you need to replace `<your-docker-username>` with your Docker Hub username.

## Environment Variables

|Variable Name                    |Description                         |
|---------------------------------|------------------------------------|
|ENV_STATE                        |Environment state (e.g., dev, prod) |
|DEV_OPENAM_CLIENT_ID             |OpenAM client ID                    |
|DEV_OPENAM_CLIENT_SECRET         |OpenAM client secret                |
|DEV_OPENAM_OIDC_BASE_URL         |OpenAM OIDC base URL                |
|DEV_OPENAM_OIDC_USERINFO_URL     |OpenAM OIDC userinfo URL            |
|DEV_SISCAT_DB_SERVER_HOST        |PostgreSQL server host              |
|DEV_SISCAT_DB_SERVER_PORT        |PostgreSQL server port              |
|DEV_SISCAT_DB_NAME	PostgreSQL    |database name                       |
|DEV_SISCAT_DB_USER	PostgreSQL    |database user                       |
|DEV_SISCAT_DB_PASSWORD           |PostgreSQL database password        |

## API Endpoints

The [Swagger](https://swagger.io/) documentation is available at the following endpoint:

`/siscat/api/v1/docs`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
