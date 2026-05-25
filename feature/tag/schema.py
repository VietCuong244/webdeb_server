from pydantic import BaseModel

class TagBase(BaseModel):
    name: str
    description: str | None = None
    is_active: bool = True
    
