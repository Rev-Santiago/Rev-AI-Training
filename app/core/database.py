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

def init_db():
    """Initializes tables and seeds default personas"""
    from app.models import Base, Persona
    Base.metadata.create_all(bind=engine)
    
    # Seeding logic for your Grade 1-7 and TVET personas
    db = SessionLocal()
    if not db.query(Persona).first():
        defaults = {
            "Grade 7": "Mentor vibe. Use detailed facts...",
            "TVET": "Professional yet easy to understand for career shifter..."
        }
        for level, desc in defaults.items():
            db.add(Persona(grade_level=level, description=desc))
        db.commit()
    db.close()