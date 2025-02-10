from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class TicketReport(BaseModel):
    class IssueType(str, Enum):
        BUG = "bug"
        EVOLUTION = "evolution"
        USER = "user"

    class Domain(str, Enum):
        MATCHING = "matching"
        DATA_PULL = "data_pull"
        SEARCH = "search"
        REPORTS = "reports"

    id: str
    name: str
    actor: str
    summary: str
    solution: str
    issue_type: IssueType
    domain: Domain
    ticket_url: str
    ticket_created_at: datetime
    ticket_updated_at: datetime
    created_at: datetime
