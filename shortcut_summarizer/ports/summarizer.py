from abc import ABC
from typing import List


class SummarizerPort(ABC):
    def summarize_tickets(self, tickets: List[dict]) -> dict:
        pass
