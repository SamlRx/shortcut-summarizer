from datetime import datetime
from typing import List

from pydantic import BaseModel


class Comment(BaseModel):
    actor: str
    content: str
    created: datetime


class Ticket(BaseModel):
    id: str
    title: str
    comments: List[Comment]


class TicketReport(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    actor: str
    summary: str
    solution: str
    issue: str
    part_of_the_code: str
