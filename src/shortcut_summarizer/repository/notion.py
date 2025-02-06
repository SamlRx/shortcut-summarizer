import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Type

from notion_client import Client
from pydantic import BaseModel

from shortcut_summarizer.ports.report import ReportPort

_LOGGER = logging.getLogger(__name__)


class NotionSchemaConverter:
    notion_types: Dict[Type, str] = {
        str: "rich_text",
        int: "number",
        float: "number",
        datetime: "date",
    }

    def to_notion_entry(self, data: BaseModel) -> Dict[str, Any]:
        return {}

    def to_notion_schema(self, model: Type[BaseModel]) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        fields = list(model.__annotations__.items())

        if not fields:
            return properties

        first_field_name, first_field = fields[0]
        properties[first_field_name] = {"title": {}}

        for field_name, field in fields[1:]:
            properties[field_name] = self._convert_field(field, None)

        return properties

    def _convert_field(
        self, field: Type, value: Optional[Any]
    ) -> Dict[str, Any]:
        if issubclass(field, Enum):
            options = [
                {"name": option.value, "color": "default"} for option in field
            ]
            return {
                "type": "select",
                "select": {"options": options},
            }
        elif field in self.notion_types:
            return (
                {self.notion_types[field]: {}}
                if value is None
                else {self.notion_types[field]: {"content": value}}
            )

        _LOGGER.warning(f"Unsupported field type: {field}")
        return {"rich_text": {value}}


class NotionRepository(ReportPort):

    @staticmethod
    def build(api_key: str) -> "NotionRepository":
        return NotionRepository(Client(auth=api_key))

    def __init__(
        self,
        client: Client,
        schema_converter: NotionSchemaConverter = NotionSchemaConverter(),
    ) -> None:
        self._client = client
        self._schema_converter = schema_converter

    def _get_table(self, table_name: str) -> Optional[Dict[str, Any]]:
        results = self._client.search(
            query=table_name,
            filter={"property": "object", "value": "database"},
        ).get("results")
        if not results:
            return None
        return results[0]

    def init_table(
        self, database_name: str, table_name: str, model: BaseModel.__class__
    ) -> bool:
        parent_page_id = self._get_parent_page_id(database_name)
        if not parent_page_id:
            _LOGGER.error(f"Parent page '{database_name}' not found.")
            return False

        if self._get_table(parent_page_id):
            _LOGGER.debug(f"Table '{table_name}' already exists.")
            return True

        return bool(self._create_table(model, parent_page_id, table_name))

    def _create_table(
        self, model: BaseModel.__class__, parent_page_id: str, table_name: str
    ) -> bool:
        database = {
            "parent": {"type": "page_id", "page_id": parent_page_id},
            "title": [
                {"type": "text", "text": {"content": table_name, "link": None}}
            ],
            "properties": self._schema_converter.to_notion_schema(model),
        }
        _LOGGER.info(f"Creating table '{table_name}'...")
        return bool(self._client.databases.create(**database))

    def _create_parent_page(self, database_name: str) -> None:
        self._client.pages.create(
            parent={"type": "workspace"},
            properties={
                "title": [{"type": "text", "text": {"content": database_name}}]
            },
        )

    def _get_parent_page_id(self, database_name: str) -> Optional[str]:
        if results := (
            self._client.search(
                query=database_name,
                filter={"property": "object", "value": "page"},
            ).get("results")
        ):
            return results[0]["id"]

        _LOGGER.info(f"Database '{database_name}' not found.")
        return None

    def get_last_entry_date(self) -> datetime:
        return datetime.now()

    def save_entry(
        self, database_name: str, table_name: str, data: BaseModel
    ) -> None:
        parent_page_id = self._get_parent_page_id(database_name)
        if not parent_page_id:
            raise ValueError(f"Parent page '{database_name}' not found.")

        table = self._get_table(table_name)
        if not table:
            raise ValueError(
                f"Table '{table_name}' not found in database '{database_name}'"
            )

        self._client.pages.create(
            parent={"database_id": table.get("id")},
            properties=self._schema_converter.to_notion_entry(data),
        )
        _LOGGER.debug(f"New entry saved in table '{table_name}'.")
