from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

# Factory logic for Database Selection
DB_TYPE = os.getenv("DB_TYPE", "sqlite")
SQLITE_URL = "sqlite:////app/data/guro.db"
POSTGRES_URL = os.getenv("DATABASE_URL") # For production use

def get_engine():
    if DB_TYPE == "postgresql":
        # Provide a fallback or raise an error if the URL is missing
        url = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/dbname")
        return create_engine(url)
    
    # NEW: Support for MySQL
    elif DB_TYPE == "mysql":
        # Provide a fallback or raise an error if the URL is missing
        url = os.getenv("DATABASE_URL", "mysql+pymysql://user:pass@localhost:3306/dbname")
        return create_engine(url)
    
    # Default to SQLite for local training
    return create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

engine = get_engine()
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