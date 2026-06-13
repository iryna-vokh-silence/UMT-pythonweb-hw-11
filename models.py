from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Date, Text
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    avatar = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    contacts = relationship("Contact", back_populates="owner")

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    email = Column(String, index=True, nullable=False)
    phone = Column(String, nullable=False)
    birthday = Column(Date, nullable=False)
    additional_data = Column(Text, nullable=True)
    
    # Зв'язок з користувачем
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", back_populates="contacts")
    