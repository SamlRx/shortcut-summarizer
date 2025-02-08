from unittest.mock import MagicMock, create_autospec

import pytest

from shortcut_summarizer.domains.ticket import Ticket
from shortcut_summarizer.ports.report import ReportPort
from shortcut_summarizer.ports.ticket import TicketPort
from shortcut_summarizer.services.fetch_ticket import FetchTicket


# Mocking the TicketPort and ReportPort interfaces
@pytest.fixture
def mock_ticket_port() -> MagicMock:
    return create_autospec(TicketPort)


@pytest.fixture
def mock_report_port() -> MagicMock:
    return create_autospec(ReportPort)


@pytest.fixture
def fetch_ticket(
    mock_ticket_port: MagicMock, mock_report_port: MagicMock
) -> FetchTicket:
    return FetchTicket(
        ticket_project_name="test_project",
        database_name="test_database",
        ticket_repository=mock_ticket_port,
        report_repository=mock_report_port,
        report_model=Ticket,
    )


def test_team_id_cached_property(
    fetch_ticket: FetchTicket, mock_ticket_port: MagicMock
) -> None:
    # GIVEN
    mock_ticket_port.get_team_id.return_value = "team_123"

    # WHEN
    team_id = fetch_ticket._team_id

    # THEN
    assert team_id == "team_123"
    mock_ticket_port.get_team_id.assert_called_once_with(
        fetch_ticket._ticket_project_name
    )


def test_fetch_tickets(
    fetch_ticket: FetchTicket,
    mock_ticket_port: MagicMock,
    mock_report_port: MagicMock,
) -> None:
    # GIVEN
    mock_ticket_port.get_team_id.return_value = "team_123"
    mock_report_port.get_last_entry_date.return_value = "2023-01-01"

    tickets = [
        MagicMock(spec=Ticket),
        MagicMock(spec=Ticket),
    ]
    mock_ticket_port.fetch_tickets_from_project_since.return_value = iter(
        tickets
    )

    # WHEN
    result = list(fetch_ticket())

    # THEN
    assert result == tickets
    mock_ticket_port.get_team_id.assert_called_once_with(
        fetch_ticket._ticket_project_name
    )
    mock_report_port.get_last_entry_date.assert_called_once()
    mock_ticket_port.fetch_tickets_from_project_since.assert_called_once_with(
        "team_123", "2023-01-01"
    )


def test_fetch_tickets_no_tickets(
    fetch_ticket: FetchTicket,
    mock_ticket_port: MagicMock,
    mock_report_port: MagicMock,
) -> None:
    # Arrange
    mock_ticket_port.get_team_id.return_value = "team_123"
    mock_report_port.get_last_entry_date.return_value = "2023-01-01"

    mock_ticket_port.fetch_tickets_from_project_since.return_value = iter([])

    # Act
    result = list(fetch_ticket())

    # Assert
    assert result == []
    mock_ticket_port.get_team_id.assert_called_once_with(
        fetch_ticket._ticket_project_name
    )
    mock_report_port.get_last_entry_date.assert_called_once()
    mock_ticket_port.fetch_tickets_from_project_since.assert_called_once_with(
        "team_123", "2023-01-01"
    )
