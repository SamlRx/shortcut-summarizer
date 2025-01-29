from datetime import datetime
from unittest.mock import MagicMock, call

import pytest

from shortcut_summarizer.repository.shortcut import TicketRepository


@pytest.fixture
def mock_requests_get() -> MagicMock:
    return MagicMock()


@pytest.fixture
def ticket_repository(mock_requests_get: MagicMock) -> TicketRepository:
    return TicketRepository(
        api_key="fake-api-key",
        api_url="https://api.shortcut.com/api/v3",
        get=mock_requests_get,
    )


def test_get_team_id(
    ticket_repository: TicketRepository, mock_requests_get: MagicMock
) -> None:
    # Given: A mocked response for the "groups" endpoint containing multiple
    # teams
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"id": "team-id-1", "name": "Team One"},
        {"id": "team-id-2", "name": "strike-tickets"},
    ]
    mock_requests_get.return_value = mock_response

    # When: The get_team_id method is called with the name "strike-tickets"
    team_id = ticket_repository.get_team_id("strike-tickets")

    # Then: The correct team ID is returned, and the endpoint is called once
    assert team_id == "team-id-2"
    mock_requests_get.assert_called_once_with("groups")


def test_fetch_tickets_from_project_since(
    ticket_repository: TicketRepository, mock_requests_get: MagicMock
) -> None:
    # Given: A mocked response for tickets updated since a specific date for
    # a team
    team_id = "team-id-1"
    since = datetime(2025, 1, 1)

    mock_response_1 = MagicMock()
    mock_response_1.status_code = 200
    mock_response_1.json.return_value = {
        "data": [
            {
                "id": "ticket-id-1",
                "name": "Ticket One",
                "created_at": "2025-01-02T00:00:00Z",
                "updated_at": "2025-01-02T00:00:00Z",
                "description": "This is a ticket description",
            }
        ],
        "next": None,
    }

    mock_response_2 = MagicMock()
    mock_response_2.status_code = 200
    mock_response_2.json.return_value = {
        "data": [
            {
                "id": "comment-1",
                "text": "foo bar baz",
                "author": "DarK Vador",
                "created_at": "2025-01-03T00:00:00Z",
            }
        ],
        "next": "foo",
    }
    mock_response_3 = MagicMock()
    mock_response_3.status_code = 200
    mock_response_3.json.return_value = {
        "data": [
            {
                "id": "comment-2",
                "text": "platypus",
                "author": "Not so Dark Vador",
                "created_at": "2025-01-04T00:00:00Z",
            }
        ],
        "next": None,
    }

    mock_requests_get.side_effect = [
        mock_response_1,
        mock_response_2,
        mock_response_3,
    ]

    # When: The fetch_tickets_from_project_since method is called with the
    # team ID and date
    tickets = list(
        ticket_repository.fetch_tickets_from_project_since(team_id, since)
    )

    # Then: The returned tickets match the mocked response, and the API
    # is called
    assert len(tickets) == 1
    assert tickets[0].id == "ticket-id-1"
    assert tickets[0].name == "Ticket One"
    assert tickets[0].description == "This is a ticket description"
    assert len(tickets[0].comments) == 2
    assert tickets[0].comments[0].id == "comment-1"
    assert tickets[0].comments[0].text == "foo bar baz"
    assert tickets[0].comments[0].author == "DarK Vador"
    assert tickets[0].comments[1].id == "comment-2"
    assert tickets[0].comments[1].text == "platypus"
    assert tickets[0].comments[1].author == "Not so Dark Vador"

    assert mock_requests_get.call_count == 3

    assert mock_requests_get.call_args_list[0] == call(
        "https://api.shortcut.com/api/v3/search/stories",
        headers={"Shortcut-Token": "fake-api-key"},
        params={
            "query": "team:team-id-1 updated-after:2025-01-01 00:00:00",
            "page_size": 100,
        },
    )
    assert mock_requests_get.call_args_list[1] == call(
        "https://api.shortcut.com/api/v3/stories/ticket-id-1/comments",
        headers={"Shortcut-Token": "fake-api-key"},
        params={"page_size": 100},
    )
    assert mock_requests_get.call_args_list[2] == call(
        "https://api.shortcut.com/api/v3/stories/ticket-id-1/comments",
        headers={"Shortcut-Token": "fake-api-key"},
        params={"page_size": 100, "next": "foo"},
    )
