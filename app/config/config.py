from typing import Optional

from loguru import logger
from pydantic import BaseSettings, Field


logger = logger.bind(name="app.core.config")


class GlobalConfig(BaseSettings):
    """Global configurations."""

    # This variable will be loaded from the .env file.
    # However, if there is a shell environment variable
    # having the same name, that will take precedence.

    ENV_STATE: Optional[str] = Field(None, env="ENV_STATE")
    LOG_PATH: Optional[str] = Field(None, env="LOG_PATH")
    LOG_FILENAME: Optional[str] = Field(None, env="LOG_FILENAME")
    LOG_ROTATION: Optional[str] = Field(None, env="LOG_ROTATION")
    LOG_RETENTION: Optional[str] = Field(None, env="LOG_RETENTION")
    LOG_FORMAT: Optional[str] = Field(None, env="LOG_FORMAT")

    class Config:
        """Loads the dotenv file."""

        env_file: str = ".env"


class DevConfig(GlobalConfig):
    """Development configurations."""

    ROOT_PATH: Optional[str] = Field(None, env="DEV_ROOT_PATH")
    LOG_LEVEL: Optional[str] = Field(None, env="DEV_LOG_LEVEL")
    OPENAM_CLIENT_ID: Optional[str] = Field(
        None,
        env="DEV_OPENAM_CLIENT_ID",
    )
    OPENAM_CLIENT_SECRET: Optional[str] = Field(
        None,
        env="DEV_OPENAM_CLIENT_SECRET",
    )
    OPENAM_OIDC_BASE_URL: Optional[str] = Field(
        None,
        env="DEV_OPENAM_OIDC_BASE_URL",
    )
    OPENAM_OIDC_USERINFO_URL: Optional[str] = Field(
        None,
        env="DEV_OPENAM_OIDC_USERINFO_URL",
    )
    OPENAM_OIDC_WELL_KNOWN_CONTEXT: Optional[str] = Field(
        None,
        env="DEV_OPENAM_OIDC_WELL_KNOWN_CONTEXT",
    )
    SISCAT_WHITELIST_DIPENDENTE: Optional[str] = Field(
        None,
        env="DEV_SISCAT_WHITELIST_DIPENDENTE",
    )
    SISCAT_DB_SERVER_HOST: Optional[str] = Field(
        None, env="DEV_SISCAT_DB_SERVER_HOST"
    )
    SISCAT_DB_SERVER_PORT: Optional[str] = Field(
        None, env="DEV_SISCAT_DB_SERVER_PORT"
    )
    SISCAT_DB_NAME: Optional[str] = Field(
        None, env="DEV_SISCAT_DB_NAME"
    )
    SISCAT_DB_USER: Optional[str] = Field(
        None, env="DEV_SISCAT_DB_USER"
    )
    SISCAT_DB_PASSWORD: Optional[str] = Field(
        None, env="DEV_SISCAT_DB_PASSWORD"
    )



class ProdConfig(GlobalConfig):
    """Production configurations."""

    ROOT_PATH: Optional[str] = Field(None, env="PROD_ROOT_PATH")
    LOG_LEVEL: Optional[str] = Field(None, env="PROD_LOG_LEVEL")
    LOCAL_STORAGE_BASEPATH: Optional[str] = Field(
        None,
        env="PROD_LOCAL_STORAGE_BASEPATH"
    )
    OPENAM_CLIENT_ID: Optional[str] = Field(
        None,
        env="PROD_OPENAM_CLIENT_ID",
    )
    OPENAM_CLIENT_SECRET: Optional[str] = Field(
        None,
        env="PROD_OPENAM_CLIENT_SECRET",
    )
    OPENAM_OIDC_BASE_URL: Optional[str] = Field(
        None,
        env="PROD_OPENAM_OIDC_BASE_URL",
    )
    OPENAM_OIDC_USERINFO_URL: Optional[str] = Field(
        None,
        env="PROD_OPENAM_OIDC_USERINFO_URL",
    )
    OPENAM_OIDC_WELL_KNOWN_CONTEXT: Optional[str] = Field(
        None,
        env="PROD_OPENAM_OIDC_WELL_KNOWN_CONTEXT",
    )
    SISCAT_WHITELIST_DIPENDENTE: Optional[str] = Field(
        None,
        env="PROD_SISCAT_WHITELIST_DIPENDENTE",
    )
    SISCAT_DB_SERVER_HOST: Optional[str] = Field(
        None, env="PROD_SISCAT_DB_SERVER_HOST"
    )
    SISCAT_DB_SERVER_PORT: Optional[str] = Field(
        None, env="PROD_SISCAT_DB_SERVER_PORT"
    )
    SISCAT_DB_NAME: Optional[str] = Field(
        None, env="PROD_SISCAT_DB_NAME"
    )
    SISCAT_DB_USER: Optional[str] = Field(
        None, env="PROD_SISCAT_DB_USER"
    )
    SISCAT_DB_PASSWORD: Optional[str] = Field(
        None, env="PROD_SISCAT_DB_PASSWORD"
    )


class FactoryConfig:
    """Returns a config instance dependending on the ENV_STATE variable."""

    def __init__(self, env_state: Optional[str]):
        self.env_state = env_state

    def __call__(self):
        if self.env_state == "dev":
            return DevConfig()

        elif self.env_state == "prod":
            return ProdConfig()


configuration = FactoryConfig(GlobalConfig().ENV_STATE)()
logger.debug(f"Global config: {configuration.__repr__()}")
