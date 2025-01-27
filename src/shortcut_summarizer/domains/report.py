from datetime import datetime

from pydantic import BaseModel

class TicketReport(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    actor: str
    summary: str
    solution: str
    issue: str
    part_of_the_code: str
