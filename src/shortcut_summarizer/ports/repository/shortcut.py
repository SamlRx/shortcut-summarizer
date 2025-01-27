import logging
from datetime import datetime
from typing import Callable, Iterator, Dict

import requests

from shortcut_summarizer.domains.ticket import Ticket
from shortcut_summarizer.ports.ticket import TicketPort

_LOGGER = logging.getLogger(__name__)

class TicketRepository(TicketPort):
    def __init__(
        self, api_key: str, api_url: str, get: Callable = requests.get
    ) -> None:
        self._api_key = api_key
        self._api_url = api_url
        self._get = get

    def _headers(self) -> Dict:
        return {"Shortcut-Token": self._api_key}

    def fetch_data_from_project_since(self, project_name: str, since: datetime) -> Iterator[Ticket]:
        _LOGGER.info("Fetching info from %s", project_name)
        response = self._get(
            f"{self._api_url}/stories", headers=self._headers()
        )
        if response.status_code == 200:
            yield from response.json()
        else:
            _LOGGER.error(
                "Error fetching tickets:", response.status_code, response.text
            )