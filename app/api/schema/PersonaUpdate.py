# Schema for adding/updating personas
from pydantic import BaseModel

class PersonaUpdate(BaseModel):
    grade_level: str
    description: str
