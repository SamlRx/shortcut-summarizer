from datetime import datetime
from typing import Callable, List

import requests
from domains.models import Ticket
from ports.ticket import TicketPort


class TicketRepository(TicketPort):
    def __init__(
        self, api_key: str, api_url: str, get: Callable = requests.get
    ) -> None:
        self._api_key = api_key
        self._api_url = api_url
        self._get = get

    def _headers(self):
        return {"Shortcut-Token": self._api_key}

    def fetch_tickets(self) -> dict:
        """Fetch bug tickets from Shortcut."""
        response = self._get(
            f"{self._api_url}/stories", headers=self._headers()
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(
                "Error fetching tickets:", response.status_code, response.text
            )
            return {}

    def fetch_data_from_project_since(self, project_name: str, since: datetime) -> List[dict]:
        """Fetch bug tickets from Shortcut."""
        response = self._get(
            f"{self._api_url}/stories", headers=self._headers()
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(
                "Error fetching tickets:", response.status_code, response.text
            )
            return {}