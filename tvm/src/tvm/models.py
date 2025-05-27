from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")  # 'admin' or 'user'


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    user_id = Column(Integer, index=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class Category(Base):
    __tablename__ = "categories"
    name = Column(String, primary_key=True, index=True)

class SubCategory(Base):
    __tablename__ = "sub_categories"
    name = Column(String, primary_key=True, index=True)

class AdvisoryText(Base):
    __tablename__ = "advisory_texts"
    category_name = Column(String, ForeignKey("categories.name"), primary_key=True)
    sub_category_name = Column(String, ForeignKey("sub_categories.name"), primary_key=True)
    text = Column(String)

class InputData(BaseModel):
    input: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str