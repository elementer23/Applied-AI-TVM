from models import Base
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import subprocess

from sqlalchemy.engine.url import make_url
import embedchain.loaders.mysql as mysql_loader_module

_original_init = mysql_loader_module.MySQLLoader.__init__
load_dotenv()

def patched_init(self, config):
    url = config.get("url")
    if url:
        parsed_url = make_url(url)
        config = {
            "host": parsed_url.host,
            "user": parsed_url.username,
            "password": parsed_url.password,
            "port": parsed_url.port,
            "database": parsed_url.database,
        }

    _original_init(self, config)


mysql_loader_module.MySQLLoader.__init__ = patched_init

SQLALCHEMY_DATABASE_URL = os.getenv("SQL_CONNECTION")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def reset_database():
    """
    Truncate selected tables and reset auto-increment counters.
    """
    tables_to_truncate = [
        "advisory_texts",
        "categories",
        "sub_categories"
    ]

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))

            for table in tables_to_truncate:
                conn.execute(text(f"TRUNCATE TABLE {table};"))

            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            trans.commit()
        except Exception as e:
            trans.rollback()
            print("Failed to reset database:", e)
            raise


def run_init_db():
    subprocess.run(["python", "init_db.py"], check=True)