from getpass import getpass

from dotenv import load_dotenv
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from models import User


load_dotenv(dotenv_path="../../.env")
SQLALCHEMY_DATABASE_URL = os.getenv("SQL_CONNECTION")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin():
    db = SessionLocal()

    print("Create initial admin user")

    username = input("Enter admin username: ").strip()
    if db.query(User).filter(User.username == username).first():
        print("Username already exists.")
        db.close()
        return

    password = getpass("Enter admin password: ").strip()
    confirm_password = getpass("Confirm password: ").strip()

    if password != confirm_password:
        print("Passwords do not match.")
        db.close()
        return

    hashed_password = get_password_hash(password)
    admin_user = User(username=username, hashed_password=hashed_password, role="admin")
    db.add(admin_user)
    db.commit()
    db.close()
    print(f"Admin user '{username}' created successfully.")


def get_password_hash(password):
    return pwd_context.hash(password)


if __name__ == "__main__":
    create_admin()
