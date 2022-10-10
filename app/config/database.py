from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.config import configuration as cfg


SQLALCHEMY_DATABASE_URL = f"""\
postgresql://{cfg.SISCAT_DB_USER}:{cfg.SISCAT_DB_PASSWORD}@\
{cfg.SISCAT_DB_SERVER_HOST}:{cfg.SISCAT_DB_SERVER_PORT}/{cfg.SISCAT_DB_NAME}\
"""

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

