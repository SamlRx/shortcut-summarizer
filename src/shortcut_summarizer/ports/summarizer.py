from abc import ABC, abstractmethod
from typing import List

from shortcut_summarizer.domains.ticket import Ticket


class SummarizerPort(ABC):
    @abstractmethod
    def summarize_tickets(self, tickets: List[Ticket]) -> dict:
        pass
