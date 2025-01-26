from typing import List

from domain.models import TicketReport, Ticket
from ports.summarizer import SummarizerPort
from services.models import Step, T, V


class ReportBuilder(Step):

    def __init__(self, summarizer: SummarizerPort):
        self._summarizer = summarizer


    def execute(self, data: List[Ticket]) -> List[TicketReport]:
        pass

    def _build_report(self, payload:dict) -> TicketReport:
        pass
