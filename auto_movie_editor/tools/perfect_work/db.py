from sqlalchemy import create_engine, Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, Session, declarative_base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from passlib.context import CryptContext
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Database setup
DATABASE_URL = "sqlite:///./test.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    permissions = Column(String)  # Comma-separated list
    created_at = Column(DateTime, default=datetime.utcnow)
    
    images = relationship("ImageDetail", back_populates="author")

class ImageDetail(Base):
    __tablename__ = "image_details"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    author_id = Column(String, ForeignKey("users.id"))
    image_url = Column(String)
    resolution = Column(String)
    download_engine = Column(String, nullable=True)
    site_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved = Column(Boolean, default=False)
    
    author = relationship("User", back_populates="images")

Base.metadata.create_all(bind=engine)

# Pydantic models
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    permissions: List[str] = []

class UserOut(BaseModel):
    id: str
    name: str
    email: str
    permissions: List[str]
    created_at: datetime

class ImageDetailCreate(BaseModel):
    title: str
    image_url: str
    resolution: Optional[str] = None
    download_engine: Optional[str] = None
    site_url: str

class ImageDetailOut(BaseModel):
    id: str
    title: str
    author: UserOut
    image_url: str
    resolution: str
    download_engine: Optional[str]
    site_name: str
    site_url: str
    created_at: datetime
    approved: bool
    