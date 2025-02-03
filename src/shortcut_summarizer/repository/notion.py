import logging
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Type
from typing import Optional

from notion_client import Client, APIResponseError
from pydantic import BaseModel

from shortcut_summarizer.ports.report import ReportPort

_LOGGER = logging.getLogger(__name__)


class NotionSchemaConverter:
    notion_types = {
        str: {"type": "rich_text"},
        int: {"type": "number"},
        float: {"type": "number"},
        datetime: {"type": "date"},
        Enum: {"type": "select"},
    }

    def to_notion_schema(self, model: Type[BaseModel]) -> Dict[str, Any]:
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
            elif field in self.notion_types:
                properties[field_name] = self.notion_types[field]
            else:
                properties[field_name] = {"type": "rich_text"}

        return properties


class NotionRepository(ReportPort):

    @staticmethod
    def build(api_key: str) -> "NotionRepository":
        return NotionRepository(Client(auth=api_key))

    def __init__(self, client: Client, schema_converter: NotionSchemaConverter = NotionSchemaConverter()) -> None:
        self._client = client
        self._schema_converter = schema_converter

    def _exist_table(
            self, parent_page_id: str, table_name: str
    ) -> bool:
        results = (self._client.search(query=table_name,
                                       filter={"property": "object", "value": "database"})
                    .get('results'))
        if not results:
            return False
        return True

    def init_table(
            self, database_name: str, table_name: str, model: BaseModel.__class__
    ) -> bool:
        parent_page_id = self._get_parent_page_id(database_name)
        if not parent_page_id:
            return False

        if self._exist_table(parent_page_id, table_name):
            _LOGGER.info(f"Table '{table_name}' already exists.")
            return True

        return self._create_table(model, parent_page_id, table_name)

    def _create_table(self, model, parent_page_id, table_name):
        database = {
            "parent": {"type": "page_id", "page_id": parent_page_id},
            "title": [{"type": "text", "text": {"content": table_name}}],
            "properties": self._schema_converter.to_notion_schema(model),
        }
        return bool(self._client.databases.create(**database))

    def _create_parent_page(self, database_name: str) -> None:
        self._client.pages.create(
            parent={"type": "workspace"},
            properties={"title": [{"type": "text", "text": {"content": database_name}}]},
        )

    def _get_parent_page_id(self, database_name: str) -> Optional[str]:
        if page_id := (
                self._client.search(
                    query=database_name,
                    filter={"property": "object", "value": "page"})
                        .get('results')
                [0]
                        .get("id")
        ):
            return page_id

        _LOGGER.info(f"Database '{database_name}' not found.")
        return None

    def get_last_entry_date(self) -> datetime:
        return datetime.now()

    def save_entry(
            self, database_name: str, table_name: str, data: BaseModel
    ) -> None:
        pass
