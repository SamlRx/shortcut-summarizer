from datetime import datetime
from typing import List

from pydantic import BaseModel


class Comment(BaseModel):
    id: str
    author: str
    text: str
    created_at: datetime


class Ticket(BaseModel):
    id: str
    name: str
    created_at: datetime
    updated_at: datetime
    description: str
    comments: List[Comment]
