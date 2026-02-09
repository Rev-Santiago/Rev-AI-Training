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
    # CRITICAL: Local import registers your tables with SQLAlchemy
    import app.models 
    from app.models import Base, Persona
    
    # Now this command builds the 'personas' and 'chat_history' tables
    Base.metadata.create_all(bind=engine) 
    
    db = SessionLocal()
    try:
        # Check if we need to seed the TVET and Grade 7 personas
        if not db.query(Persona).first():
            defaults = {
                "Grade 7": "Mentor vibe. Use detailed facts, proper terminology, and social analogies.",
                "TVET": "Professional yet easy to understand for career shifter, or beginner, assuming technical skill based vocational education."
            }
            for level, desc in defaults.items():
                db.add(Persona(grade_level=level, description=desc))
            db.commit()
    finally:
        db.close()