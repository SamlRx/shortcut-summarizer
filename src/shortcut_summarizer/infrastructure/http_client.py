from typing import Any, Callable, Dict, Optional

import requests


class HttpClient:

    def __init__(self, get: Callable = requests.get) -> None:
        self._get = get


    def get(self, url: str, headers: Optional[Dict]) -> Optional[Any]:
        if headers:
            response = self._get(url, headers=headers)
        else:
            response = self._get(url)

        if response.status_code == 200:
            return response.json()