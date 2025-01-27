from typing import List, Iterator, Iterable

from shortcut_summarizer.domains.report import TicketReport
from shortcut_summarizer.domains.ticket import Ticket
from shortcut_summarizer.ports.summarizer import SummarizerPort
from shortcut_summarizer.services.models import Step
from functional import seq

class SummarizeTicket(Step):
    def __init__(self, summarizer: SummarizerPort):
        self._summarizer = summarizer

    def __call__(self, data: Iterable[Ticket]) -> Iterator[TicketReport]:
        values: List[TicketReport] = (
            seq(data)
            .map(self._summarizer.summarize_tickets)
            .to_list()
        )
        yield from values
