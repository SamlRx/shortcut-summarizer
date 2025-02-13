from abc import ABC, abstractmethod
from typing import Optional

from shortcut_summarizer.domains.report import TicketReport
from shortcut_summarizer.domains.ticket import Ticket


class SummarizerPort(ABC):

    @abstractmethod
    def classify_domain(self, ticket: Ticket) -> Optional[TicketReport.Domain]:
        pass

    @abstractmethod
    def summarize_ticket(self, ticket: Ticket) -> Optional[str]:
        pass

    @abstractmethod
    def extract_solution(self, ticket: Ticket) -> Optional[str]:
        pass

    @abstractmethod
    def classify_issue_type(
        self, ticket: Ticket
    ) -> Optional[TicketReport.IssueType]:
        pass
