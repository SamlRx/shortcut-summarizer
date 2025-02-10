from abc import ABC, abstractmethod

from shortcut_summarizer.domains.report import TicketReport
from shortcut_summarizer.domains.ticket import Ticket


class SummarizerPort(ABC):
    @abstractmethod
    def summarize(self, tickets: Ticket) -> TicketReport:
        pass
