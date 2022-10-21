# Catasto API

Repo for georoma catasto api. It depends on Catasto Postgres database available [here](https://github.com/catasto-open/catasto-db/tree/develop) and on GeoRoma OpenAM server.

## To run with docker

Build with 

```
docker build . -t catasto-api --no-cache
```
 You can run it simply with

```
 docker run -p 80:80 catasto-api
 ```
But to make it functional you need to provide the env variables pointing to required services:


- ENV_STATE=dev

- DEV_OPENAM_CLIENT_ID
- DEV_OPENAM_CLIENT_SECRET
- DEV_OPENAM_OIDC_BASE_URL
- DEV_OPENAM_OIDC_USERINFO_URL

- DEV_SISCAT_DB_SERVER_HOST
- DEV_SISCAT_DB_SERVER_PORT
- DEV_SISCAT_DB_NAME
- DEV_SISCAT_DB_USER
- DEV_SISCAT_DB_PASSWORD


## To run locally

### Static files
Create the folder /app/app on your machine and copy the folder /app/templates inside it (then you'll have /app/app/templates)

### From the project folder
```
poetry shell
poetry run uvicorn app.main:app --host 0.0.0.0 --port 5000
```

The swagger interface will be available at

`http://localhost:5000/siscat/api/v1/docs`

