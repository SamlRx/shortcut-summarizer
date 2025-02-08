from functools import cached_property
from typing import Iterator, Type

from pydantic import BaseModel

from shortcut_summarizer.domains.report import TicketReport
from shortcut_summarizer.domains.ticket import Ticket
from shortcut_summarizer.ports.report import ReportPort
from shortcut_summarizer.ports.ticket import TicketPort
from shortcut_summarizer.services._models import InitStep


class FetchTicket(InitStep):
    def __init__(
        self,
        ticket_project_name: str,
        database_name: str,
        ticket_repository: TicketPort,
        report_repository: ReportPort,
        report_model: BaseModel.__class__ = Type[TicketReport],
    ) -> None:
        self._ticket_project_name = ticket_project_name
        self._database_name = database_name
        self._ticket_repository = ticket_repository
        self._report_repository = report_repository
        self._report_model = report_model

    @cached_property
    def _team_id(self) -> str:
        return self._ticket_repository.get_team_id(self._ticket_project_name)

    def __call__(self) -> Iterator[Ticket]:
        yield from self._ticket_repository.fetch_tickets_from_project_since(
            self._team_id,
            self._report_repository.get_last_entry_date(
                self._database_name,
                self._report_model.__name__,
                self._report_model,
            ),
        )
