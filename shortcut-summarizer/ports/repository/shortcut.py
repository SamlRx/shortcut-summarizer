from typing import Callable

import requests

from domain.models import Ticket
from ports.ticket import TicketPort


class TicketRepository(TicketPort):

    def __init__(self, api_key:str, api_url:str, get: Callable=requests.get) -> None:
        self._api_key=api_key
        self._api_url=api_url
        self._get = get

    def _headers(self):
        return {"Shortcut-Token": self._api_key}

    def fetch_tickets(self) -> dict:
        """Fetch bug tickets from Shortcut."""
        response = self._get(f"{self._api_url}/stories", headers=self._headers())
        if response.status_code == 200:
            return sef._build_ticket(response.json())
        else:
            print("Error fetching tickets:", response.status_code, response.text)
            return []

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