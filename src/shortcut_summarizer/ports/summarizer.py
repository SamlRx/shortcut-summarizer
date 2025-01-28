from abc import ABC, abstractmethod
from typing import Iterable, Iterator

from shortcut_summarizer.domains.report import TicketReport
from shortcut_summarizer.domains.ticket import Ticket


class SummarizerPort(ABC):
    @abstractmethod
    def summarize_tickets(self, tickets: Ticket) -> TicketReport:
        pass
