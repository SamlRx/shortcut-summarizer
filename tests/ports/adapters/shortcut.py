import unittest
from unittest.mock import MagicMock, patch

from ports.repository.shortcut import TicketRepository


class TestShortcutRestClient(unittest.TestCase):
    def setUp(self) -> None:
        self.api_key = "test_api_key"
        self.api_url = "https://api.shortcut.com/api/v3"
        self.accessor = TicketRepository(self.api_key, self.api_url)

    def test_headers(self) -> None:
        expected_headers = {"Shortcut-Token": self.api_key}
        self.assertEqual(self.accessor._headers(), expected_headers)

    @patch("requests.get")
    def test_fetch_tickets_success(self, mock_get:MagicMock) -> None:
        # Mocking a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1, "name": "Test Ticket"}]
        mock_get.return_value = mock_response

        result = self.accessor.fetch_tickets()

        mock_get.assert_called_once_with(
            f"{self.api_url}/stories", headers=self.accessor._headers()
        )
        self.assertEqual(result, [{"id": 1, "name": "Test Ticket"}])

    @patch("requests.get")
    def test_fetch_tickets_error(self, mock_get:MagicMock) -> None:
        # Mocking an error response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        result = self.accessor.fetch_tickets()

        mock_get.assert_called_once_with(
            f"{self.api_url}/stories", headers=self.accessor._headers()
        )
        self.assertEqual(result, [])
