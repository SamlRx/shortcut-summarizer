import logging
from datetime import datetime
from typing import Callable, Dict, Iterator, List, Optional

import requests
from streamable import Stream

from shortcut_summarizer.domains.ticket import Comment, Ticket
from shortcut_summarizer.ports.ticket import TicketPort
from shortcut_summarizer.utils import extract_datetime, extract_str

_LOGGER = logging.getLogger(__name__)
_PAGE_SIZE = 100


class TicketRepository(TicketPort):

    @staticmethod
    def build(api_key: str, api_url: str) -> "TicketRepository":
        return TicketRepository(api_key, api_url)

    def __init__(
        self,
        api_key: str,
        api_url: str,
        get: Callable = requests.get,
        local_extract_str: Callable = extract_str,
        local_extract_datetime: Callable = extract_datetime,
    ) -> None:
        self._api_key = api_key
        self._api_url = api_url
        self._get = get
        self._extract_str = local_extract_str
        self._extract_datetime = local_extract_datetime

    def get_team_id(self, team_name: str) -> str:
        return list(
            Stream(self._get("groups").json())
            .filter(lambda team: team.get("name") == team_name)
            .map(lambda team: team.get("id"))
        )[0]

    def fetch_tickets_from_project_since(
        self, team_id: str, since: datetime
    ) -> Iterator[Ticket]:
        _LOGGER.info("Fetching info for %s since %s...", team_id, since)
        yield from self._get_last_tickets_since_for_team_id(since, team_id)

    def _client_get(self, uri: str, param: Optional[Dict]) -> Optional[Dict]:
        if param:
            response = self._get(
                f"{self._api_url}/{uri}",
                headers={"Shortcut-Token": self._api_key},
                params=param,
            )
        else:
            response = self._get(
                f"{self._api_url}/{uri}",
                headers={"Shortcut-Token": self._api_key},
            )
        if response.status_code == 200:
            return response.json()
        _LOGGER.error(
            f"Error fetching {uri}:", response.status_code, response.text
        )
        return None

    def _get_last_tickets_since_for_team_id(
        self, since: datetime, team_id: str
    ) -> Iterator[Ticket]:
        """Fetch all tickets for a team updated since a specific date."""
        next_page_token = None
        while True:
            data = self._fetch_tickets_page(since, team_id, next_page_token)
            if data:
                yield from self._parse_tickets(data)
                next_page_token = data.get("next")
            if not next_page_token:
                break

    def _parse_tickets(self, data: Dict) -> Iterator[Ticket]:
        yield from Stream(data.get("data", [])).filter(
            lambda ticket: ticket.get("id")
        ).map(
            lambda ticket: self._to_ticket(
                ticket, list(self._get_ticket_comments(ticket.get("id")))
            )
        )

    def _fetch_tickets_page(
        self,
        since: datetime,
        team_id: str,
        next_page_token: Optional[str] = None,
    ) -> Optional[Dict]:
        """Fetch a single page of tickets from the API."""
        query = {
            "query": f"team:{team_id} updated-after:{since}",
            "page_size": _PAGE_SIZE,
        }
        if next_page_token:
            query["next"] = next_page_token
        return self._client_get("search/stories", query)

    def _get_ticket_comments(self, ticket_id: str) -> Iterator[Comment]:
        _LOGGER.info("Fetching comments for ticket ID: %d", ticket_id)
        next_page_token = None

        while True:
            if response := self._fetch_comment_page(
                ticket_id, next_page_token
            ):
                yield from Stream(response.get("data", [])).map(
                    lambda comment: self._to_comment(comment)
                )
                next_page_token = response.get("next")
                if not next_page_token:
                    break
            else:
                _LOGGER.error(
                    "Failed to fetch comments for ticket ID: %d", ticket_id
                )
                break

    def _fetch_comment_page(
        self, ticket_id: str, next_page_token: Optional[int] = None
    ) -> Optional[Dict]:
        query = {"page_size": _PAGE_SIZE}
        if next_page_token:
            query["next"] = next_page_token
        return self._client_get(f"stories/{ticket_id}/comments", query)

    def _to_comment(self, comment_data: Dict) -> Comment:
        return Comment(
            id=self._extract_str(comment_data, "id"),
            text=self._extract_str(comment_data, "text"),
            author=self._extract_str(comment_data, "author"),
            created_at=self._extract_datetime(comment_data, "created_at"),
        )

    def _to_ticket(self, payload: Dict, comments: List[Comment]) -> Ticket:
        return Ticket(
            id=self._extract_str(payload, "id"),
            name=self._extract_str(payload, "name"),
            created_at=self._extract_datetime(payload, "created_at"),
            updated_at=self._extract_datetime(payload, "updated_at"),
            description=self._extract_str(payload, "description"),
            comments=comments,
        )
