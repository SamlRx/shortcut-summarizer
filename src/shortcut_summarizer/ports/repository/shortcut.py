import logging
from datetime import datetime
from typing import Callable, Iterator, Dict, Optional

import requests

from shortcut_summarizer.domains.ticket import Ticket, Comment
from shortcut_summarizer.ports.ticket import TicketPort
from streamable import Stream

_LOGGER = logging.getLogger(__name__)
_PAGE_SIZE = 100

class TicketRepository(TicketPort):
    def __init__(
            self, api_key: str, api_url: str, get: Callable = requests.get
    ) -> None:
        self._api_key = api_key
        self._api_url = api_url
        self._get = get

    def _get(self, uri: str, param: Optional[Dict]) -> Optional[Dict]:
        if param:
            response = self._get(f"{self._api_url}/{uri}", headers={"Shortcut-Token": self._api_key}, params=param)
        else:
            response = self._get(f"{self._api_url}/{uri}", headers={"Shortcut-Token": self._api_key})
        if response.status_code == 200:
            return response
        _LOGGER.error(
            f"Error fetching {uri}:", response.status_code, response.text
        )

    def fetch_tickets_from_project_since(self, team_name: str, since: datetime) -> Iterator[Ticket]:
        _LOGGER.info("Fetching info for %s since %s...", team_name, since)
        if team_id := self._get_team_id_from_team_name(team_name):
            yield from self._get_last_tickets_since_for_team_id(since, team_id)

    def _get_team_id_from_team_name(self, team_name: str) -> id:
        return list(
            Stream(self._get("groups").json())
            .filter(lambda team: team.get('name') == team_name)
            .map(lambda team: team.get("id"))
        )[0]

    def _get_last_tickets_since_for_team_id(self, since: datetime, id: int) -> Iterator[Ticket]:
        uri = "search/stories"
        query = {
            "query": f"team:{id} updated-after:{since}",
            "page_size": _PAGE_SIZE
        }
        all_tickets = []
        next_page_token = None
        while True:
            if next_page_token:
                query["next"] = next_page_token
            response = self._get(uri, params=query)
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
                break
            data = response.json()
            all_tickets.extend(data.get("data", []))
            next_page_token = data.get("next")
            if not next_page_token:
                break
        yield from Stream(all_tickets).map(self._to_ticket)

    def _get_ticket_comments(self, ticket_id: int) -> Iterator[Comment]:
        pass

    def _to_ticket(self, payload: dict) -> Ticket:
        pass
