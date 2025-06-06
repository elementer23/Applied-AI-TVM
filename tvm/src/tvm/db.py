from models import Base, User
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import subprocess
from passlib.context import CryptContext

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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initial_test_database():
    db = SessionLocal()

    admin_username = "test_user"
    if db.query(User).filter(User.username == admin_username).first():
        db.close()
        return
    hashed_admin_password = get_password_hash("test_pass")
    admin_user = User(username=admin_username, hashed_password=hashed_admin_password, role="admin")

    not_admin_username = "test_not_admin"
    if db.query(User).filter(User.username == not_admin_username).first():
        db.close()
        return
    hashed_user_password = get_password_hash("notadminpass")
    not_admin_user = User(username=not_admin_username, hashed_password=hashed_user_password, role="user")

    db.add(admin_user)
    db.add(not_admin_user)
    db.commit()
    db.close()

# Resets the database, used for unit testing
def reset_database():
    tables_to_truncate = [
        "advisory_texts",
        "categories",
        "sub_categories"
        # Add tables here that need to be truncated before testing
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

# Method that runs init_db.py automatically
def run_init_db():
    subprocess.run(["python", "init_db.py"], check=True)


def get_password_hash(password):
    return pwd_context.hash(password)