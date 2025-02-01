from datetime import datetime
from enum import Enum
from typing import Any, Dict

from notion_client import Client
from pydantic import BaseModel

from shortcut_summarizer.ports.report import ReportPort


class NotionRepository(ReportPort):

    @staticmethod
    def build(api_key: str) -> "NotionRepository":
        return NotionRepository(Client(auth=api_key))

    def __init__(self, client: Client) -> None:
        self._client = client

    def _exist_repository(
        self, parent_page_id: str, database_name: str
    ) -> bool:
        return True

    @staticmethod
    def _pydantic_to_notion_schema(
        model: BaseModel.__class__,
    ) -> Dict[str, Any]:
        """Convert a Pydantic model into a Notion database schema."""
        notion_types = {
            str: {"type": "rich_text"},
            int: {"type": "number"},
            float: {"type": "number"},
            datetime: {"type": "date"},
            Enum: {"type": "select"},
        }

        properties: Dict[str, Any] = {}

        for field_name, field in model.__annotations__.items():
            if issubclass(field, Enum):
                options = [
                    {"name": option.value, "color": "default"}
                    for option in field
                ]
                properties[field_name] = {
                    "type": "select",
                    "select": {"options": options},
                }
            elif field in notion_types:
                properties[field_name] = notion_types[field]
            else:
                properties[field_name] = {"type": "rich_text"}

        return properties

    def init_repository(
        self, database_name: str, table_name: str, model: BaseModel.__class__
    ) -> bool:
        parent_page_id = self._client.pages.retrieve(database_name)

        if self._exist_repository(parent_page_id, table_name):
            return True

        database = {
            "parent": {"type": "page_id", "page_id": parent_page_id},
            "title": [{"type": "text", "text": {"content": table_name}}],
            "properties": self._pydantic_to_notion_schema(model),
        }

        return bool(self._client.databases.create(**database))

    def get_last_entry_date(self) -> datetime:
        return datetime.now()

    def save_entry(
        self, database_name: str, table_name: str, data: BaseModel
    ) -> None:
        pass
