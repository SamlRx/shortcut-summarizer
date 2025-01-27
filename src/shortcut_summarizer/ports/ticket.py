from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterator

from shortcut_summarizer.domains.ticket import Ticket


class TicketPort(ABC):
    @abstractmethod
    def fetch_data_from_project_since(
        self, project_name: str, since: datetime
    ) -> Iterator[Ticket]:
        pass
