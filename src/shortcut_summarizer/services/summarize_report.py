from datetime import datetime
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
        yield from Stream(data).map(self._summarize)

    def _summarize(self, ticket: Ticket) -> TicketReport:
        return TicketReport(
            id=ticket.id,
            name=ticket.name,
            actor=ticket.comments[0].author,
            domain=self._summarizer.classify_domain(ticket),
            ticket_url=ticket.url,
            ticket_created_at=ticket.created_at,
            ticket_updated_at=ticket.updated_at,
            summary=self._summarizer.summarize_ticket(ticket),
            solution=self._summarizer.extract_solution(ticket),
            issue_type=self._summarizer.classify_issue_type(ticket),
            created_at=datetime.now(),
        )
