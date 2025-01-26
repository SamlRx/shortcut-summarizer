from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from domain.models import Ticket


class TicketPort(ABC):

    @abstractmethod
    def fetch_data(self, ticket_id: str) -> Ticket:
        pass

    def fetch_data_from_project_since(self, project_name:str, since:datetime) -> List[dict]:
        pass
