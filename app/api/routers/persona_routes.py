from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Persona
from app.api.schema.PersonaUpdate import PersonaUpdate
from typing import Optional

router = APIRouter(prefix="/personas", tags=["Personas"])

@router.get("/")
async def list_personas(db: Session = Depends(get_db)):
    db_personas = db.query(Persona).all()
    return {p.grade_level: p.description for p in db_personas}

@router.post("/")
async def save_persona(data: PersonaUpdate, db: Session = Depends(get_db)):
    existing_persona: Optional[Persona] = db.query(Persona).filter(Persona.grade_level == data.grade_level).first()
    if existing_persona:
        existing_persona.description = data.description
    else:
        db.add(Persona(grade_level=data.grade_level, description=data.description))
    db.commit()
    return {"message": f"Successfully saved {data.grade_level}"}

@router.delete("/{grade_level}")
async def delete_persona(grade_level: str, db: Session = Depends(get_db)):
    persona = db.query(Persona).filter(Persona.grade_level == grade_level).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Grade level not found")
    db.delete(persona)
    db.commit()
    return {"message": f"Deleted {grade_level}"}