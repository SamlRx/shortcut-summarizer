from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class Domain(str, Enum):
    MATCHING = "matching"
    DATA_PULL = "data_pull"
    SEARCH = "search"
    REPORTS = "reports"


class IssueType(str, Enum):
    BUG = "bug"
    EVOLUTION = "evolution"
    USER = "user"


class TicketReport(BaseModel):
    id: str
    name: str
    created_at: datetime
    updated_at: datetime
    actor: str
    summary: str
    solution: str
    issue_type: IssueType
    domain: Domain
