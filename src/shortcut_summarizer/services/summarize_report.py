from typing import Iterable, Iterator

from streamable import Stream

from shortcut_summarizer.domains.report import TicketReport
from shortcut_summarizer.domains.ticket import Ticket
from shortcut_summarizer.ports.summarizer import SummarizerPort
from shortcut_summarizer.services._models import Step


class SummarizeTicket(Step):
    def __init__(self, summarizer: SummarizerPort):
        self._summarizer = summarizer

    def __call__(self, data: Iterable[Ticket]) -> Iterator[TicketReport]:
        yield from Stream(data).map(self._summarizer.summarize)
