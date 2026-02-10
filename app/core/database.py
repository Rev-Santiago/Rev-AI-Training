from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Use an absolute-style path to ensure it hits the Docker volume mount
DATABASE_URL = "sqlite:////app/data/guro.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes tables and seeds default personas"""
    # CRITICAL: This import registers the new Mapped classes
    import app.models 
    from app.models import Base, Persona
    
    # Builds the updated 'personas' and 'chat_history' tables
    Base.metadata.create_all(bind=engine) 
    
    db = SessionLocal()
    try:
        if not db.query(Persona).first():
            defaults = {
                "Grade 7": "Mentor vibe. Use detailed facts, proper terminology, and social analogies.",
                "TVET": "Professional yet easy to understand for career shifter..."
            }
            for level, desc in defaults.items():
                db.add(Persona(grade_level=level, description=desc))
            db.commit()
    finally:
        db.close()