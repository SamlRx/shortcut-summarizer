import requests


class ShortcutAccessor:

    def __init__(self, api_key:str, api_url:str) -> None:
        self._api_key=api_key
        self._api_url=api_url

    def _headers(self):
        return {"Shortcut-Token": self._api_key}

    def fetch_tickets(self) -> dict:
        """Fetch bug tickets from Shortcut."""
        response = requests.get(f"{self._api_url}/stories", headers=self._headers())
        if response.status_code == 200:
            return response.json()
        else:
            print("Error fetching tickets:", response.status_code, response.text)
            return []

