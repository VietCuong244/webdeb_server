from pydantic import BaseModel
from uuid import UUID   

class ReportCreate(BaseModel):
    reason: str