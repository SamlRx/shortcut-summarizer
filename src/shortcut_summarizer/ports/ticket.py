from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterator

from shortcut_summarizer.domains.ticket import Ticket


class TicketPort(ABC):
    @abstractmethod
    def fetch_tickets_from_project_since(
        self, project_name: str, since: datetime
    ) -> Iterator[Ticket]:
        pass

    @abstractmethod
    def get_team_id(self, team_name: str) -> str:
        pass
