from datetime import datetime
from typing import Dict, Any


def extract_str(data: Dict[str, Any], key: str) -> str:
    """Extract a string value from a dictionary."""
    value = data.get(key)
    if not isinstance(value, str):
        raise ValueError(f"Expected a string for '{key}', got {type(value)}")
    return value


def extract_datetime(data: Dict[str, Any], key: str) -> datetime:
    """Extract a datetime value from a dictionary."""
    value = data.get(key)
    if not isinstance(value, str):  # Assuming the API returns ISO8601 strings
        raise ValueError(
            f"Expected an ISO8601 string for '{key}', got {type(value)}"
        )
    return datetime.fromisoformat(value)


def extract_int(data: Dict[str, Any], key: str) -> int:
    """Extract an integer value from a dictionary."""
    value = data.get(key)
    if not isinstance(value, int):
        raise ValueError(f"Expected an integer for '{key}', got {type(value)}")
    return value
