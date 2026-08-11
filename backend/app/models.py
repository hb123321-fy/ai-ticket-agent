from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TicketCreate(BaseModel):
    title: str
    description: str
    system: Optional[str] = ""
    environment: str = "测试"
    attempts: Optional[str] = ""
    category: Optional[str] = "无法判断"
    priority: Optional[str] = "P3"

class Ticket(BaseModel):
    id: int
    title: str
    description: str
    system: str
    environment: str
    attempts: str
    status: str = "open"
    category: str = "无法判断"
    priority: str = "P3"
    created_at: datetime
    creator_id: int = 1

class UserRole:
    DEVELOPER = "developer"
    ENGINEER = "engineer"
    ADMIN = "admin"

class User(BaseModel):
    id: int
    name: str
    role: str