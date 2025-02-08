from datetime import datetime
from enum import Enum

from shortcut_summarizer.domains.common import BaseModelWithUpdatedAt


class Domain(str, Enum):
    MATCHING = "matching"
    DATA_PULL = "data_pull"
    SEARCH = "search"
    REPORTS = "reports"


class IssueType(str, Enum):
    BUG = "bug"
    EVOLUTION = "evolution"
    USER = "user"


class TicketReport(BaseModelWithUpdatedAt):
    id: str
    name: str
    actor: str
    summary: str
    solution: str
    issue_type: IssueType
    domain: Domain
    created_at: datetime
