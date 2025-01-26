from typing import List

from domain.models import Ticket
from ports.report import ReportPort
from ports.ticket import TicketPort
from services.models import Step, T, V, InitStep
from functional import seq


class FetchTicket(InitStep):

    def __init__(self, project_name: str, ticket_repository: TicketPort, report_repository: ReportPort) -> None:
        self._project_name = project_name
        self._ticket_repository = ticket_repository
        self._report_repository = report_repository

    def execute(self) -> List[Ticket]:
        value: List[Ticket] = (
            seq(
            self._ticket_repository.fetch_data_from_project_since(
                self._project_name,
                self._report_repository.get_last_entry_date()
            ))
           .map(self._build_ticket)
           .to_list()
        )
        return value

    @staticmethod
    def _build_ticket(ticket: dict) -> Ticket:
        return Ticket(
            id=ticket["id"],
            name=ticket["name"],
            description=ticket["description"],
            status=ticket["status"],
            type=ticket["type"],
            priority=ticket["priority"],
            estimate=ticket["estimate"],
            project_id=ticket["project_id"],
            sprint_id=ticket["sprint_id"],
            epic_id=ticket["epic_id"],
            created_at=ticket["created_at"],
            updated_at=ticket["updated_at"]
        )
