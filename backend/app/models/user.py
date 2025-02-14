from pydantic import BaseModel
from typing import Optional, Dict

class User(BaseModel):
    id: str
    email: Optional[str] = None
    credentials: Optional[Dict] = None 