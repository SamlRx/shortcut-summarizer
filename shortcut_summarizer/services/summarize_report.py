from typing import List

from domains.models import Ticket, TicketReport
from ports.summarizer import SummarizerPort
from services.models import Step


class SummarizeReport(Step):
    def __init__(self, summarizer: SummarizerPort):
        self._summarizer = summarizer

    def __call__(self, data: List[Ticket]) -> List[TicketReport]:
        return []

    def _build_report(self, payload: dict) -> TicketReport:
        pass
