from typing import Iterator

from shortcut_summarizer.domains.ticket import Ticket
from shortcut_summarizer.ports.report import ReportPort
from shortcut_summarizer.ports.ticket import TicketPort
from shortcut_summarizer.services.models import InitStep


class FetchTicket(InitStep):
    def __init__(
        self,
        project_name: str,
        ticket_repository: TicketPort,
        report_repository: ReportPort,
    ) -> None:
        self._project_name = project_name
        self._ticket_repository = ticket_repository
        self._report_repository = report_repository

    def __call__(self) -> Iterator[Ticket]:
        yield from self._ticket_repository.fetch_tickets_from_project_since(
                    self._project_name,
                    self._report_repository.get_last_entry_date(),
                )
