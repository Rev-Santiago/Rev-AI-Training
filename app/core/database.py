from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
import os

# Ensure the /data directory exists for the SQLite file
DATABASE_URL = "sqlite:///./data/guro.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Database session factory for FastAPI dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# In app/core/database.py

def init_db():
    """Initializes tables and seeds default personas"""
    # 1. CRITICAL: Import the models to populate Base.metadata
    from app.models import Base, Persona, ChatMessage 
    
    # 2. Now metadata knows about 'personas' and 'chat_history' tables
    Base.metadata.create_all(bind=engine) 
    
    db = SessionLocal()
    try:
        # 3. Check if seeding is needed
        if not db.query(Persona).first():
            defaults = {
                "Grade 7": "Mentor vibe. Use detailed facts, proper terminology, and social analogies.",
                "TVET": "Professional yet easy to understand for career shifter, or beginner, and professional, assuming this is a technical skill based vocational education in the Philippines"
            }
            for level, desc in defaults.items():
                db.add(Persona(grade_level=level, description=desc))
            db.commit()
    finally:
        db.close()