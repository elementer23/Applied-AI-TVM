from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from typing import Optional
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)  # 'admin' or 'user'

    conversations = relationship("Conversation", back_populates="user")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AdvisoryText(Base):
    __tablename__ = "advisory_texts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String(255))
    sub_category = Column(String(255))
    text = Column(Text)


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), unique=True, index=True, nullable=False)

    subcategories = relationship("SubCategory", back_populates="category")


class SubCategory(Base):
    __tablename__ = "sub_categories"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id"), index=True, nullable=False)
    name = Column(String(255), nullable=False)

    category = relationship("Category", back_populates="subcategories")


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    is_user_message = Column(Boolean, nullable=False)  # True (1) if sent by user, False (0) if sent by AI
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")


class InputData(BaseModel):
    input: str
    conversation_id: Optional[int] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    content: str
    is_user_message: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AdvisoryTextResponse(BaseModel):
    id: int
    category: str
    sub_category: str
    text: str


class AdvisoryTextModel(BaseModel):
    category_id: int
    sub_category: str
    text: str


class AdvisoryTextUpdateModel(BaseModel):
    text: str


class CategoryResponse(BaseModel):
    id: int
    name: str


class CategoryModel(BaseModel):
    name: str


class SubCategoryResponse(BaseModel):
    id: int
    category_id: int
    name: str


class SubCategoryModel(BaseModel):
    name: str

      
class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

