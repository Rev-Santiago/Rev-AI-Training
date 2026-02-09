from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Persona(Base):
    __tablename__ = "personas"
    id = Column(Integer, primary_key=True, index=True)
    grade_level = Column(String, unique=True, index=True)
    description = Column(Text)

class ChatMessage(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True) # To group messages
    role = Column(String) # 'human' or 'ai'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)