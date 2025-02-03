from typing import List, Iterator, Iterable

from shortcut_summarizer.domains.report import TicketReport
from shortcut_summarizer.domains.ticket import Ticket
from shortcut_summarizer.ports.summarizer import SummarizerPort
from shortcut_summarizer.services._models import Step
from streamable import Stream


class SummarizeTicket(Step):
    def __init__(self, summarizer: SummarizerPort):
        self._summarizer = summarizer

    def __call__(self, data: Iterable[Ticket]) -> Iterator[TicketReport]:
        yield from Stream(data).map(self._summarizer.summarize_tickets)
