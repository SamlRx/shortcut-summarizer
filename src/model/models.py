from datetime import datetime
from typing import List

from pydantic import BaseModel


class Comment(BaseModel):
    actor: str
    content: str
    created: datetime


class Ticket(BaseModel):
    title: str
    comments: List[Comment]
