import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Type

from notion_client import Client
from pydantic import BaseModel

from shortcut_summarizer.domains.common import BaseModelWithUpdatedAt
from shortcut_summarizer.ports.report import ReportPort

_LOGGER = logging.getLogger(__name__)


class NotionSchemaConverter:
    class NotionType(Enum):
        RICH_TEXT = "rich_text"
        NUMBER = "number"
        DATE = "date"
        SELECT = "select"

    _types_to_notion_types: Dict[Type, NotionType] = {
        str: NotionType.RICH_TEXT,
        int: NotionType.NUMBER,
        float: NotionType.NUMBER,
        datetime: NotionType.DATE,
    }

    def to_notion_entry(self, data: BaseModel) -> Dict[str, Any]:
        """Convert a Pydantic model instance to a Notion entry."""
        return self._build_notion_properties(data.__class__, data)

    def to_notion_schema(self, model: Type[BaseModel]) -> Dict[str, Any]:
        """Convert a Pydantic model class to a Notion schema definition."""
        return self._build_notion_properties(model)

    def _build_notion_properties(
        self, model: Type[BaseModel], data: Optional[BaseModel] = None
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}
        fields = list(model.__annotations__.items())

        if not fields:
            return properties

        # Handle the first field as a "title"
        first_field_name, first_field = fields[0]
        value = getattr(data, first_field_name) if data else None
        properties[first_field_name] = {
            "title": [{"text": {"content": value}}] if value else {}
        }

        # Process the remaining fields
        for field_name, field in fields[1:]:
            value = getattr(data, field_name) if data else None
            properties[field_name] = (
                self._field_value(field, value)
                if value
                else self._field_schema(field)
            )

        return properties

    def _field_schema(self, field: Type) -> Dict[str, Any]:
        match self._types_to_notion_types.get(field):
            case NotionSchemaConverter.NotionType.RICH_TEXT:
                return {NotionSchemaConverter.NotionType.RICH_TEXT.value: {}}
            case NotionSchemaConverter.NotionType.NUMBER:
                return {NotionSchemaConverter.NotionType.NUMBER.value: {}}
            case NotionSchemaConverter.NotionType.DATE:
                return {NotionSchemaConverter.NotionType.DATE.value: {}}
            case _:
                if issubclass(field, Enum):  # ✅ Check if it's an Enum
                    options = [
                        {"name": option.value, "color": "default"}
                        for option in field
                    ]
                    return {
                        "type": NotionSchemaConverter.NotionType.SELECT.value,
                        "select": {"options": options},
                    }
                _LOGGER.error(f"Unsupported field type: {field}")
                return {NotionSchemaConverter.NotionType.RICH_TEXT.value: {}}

    def _field_value(self, field: Type, value: Any) -> Any:
        match self._types_to_notion_types.get(field):
            case NotionSchemaConverter.NotionType.RICH_TEXT:
                return {
                    NotionSchemaConverter.NotionType.RICH_TEXT.value: [
                        {"content": value}
                    ]
                }
            case NotionSchemaConverter.NotionType.NUMBER:
                return {
                    NotionSchemaConverter.NotionType.NUMBER.value: [
                        {"content": value}
                    ]
                }
            case NotionSchemaConverter.NotionType.DATE:
                return {
                    NotionSchemaConverter.NotionType.DATE.value: [
                        {"content": value.isoformat()}
                    ]
                }
            case _:
                if issubclass(field, Enum):
                    return {
                        NotionSchemaConverter.NotionType.SELECT.value: {
                            "name": value.value
                        }
                    }
                _LOGGER.error(f"Unsupported field type: {field}")
                return {
                    NotionSchemaConverter.NotionType.RICH_TEXT.value: [
                        {"content": value}
                    ]
                }


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
        self,
        database_name: str,
        table_name: str,
        model: Type[BaseModelWithUpdatedAt],
    ) -> bool:
        parent_page_id = self._get_parent_page_id(database_name)
        if not parent_page_id:
            _LOGGER.error(f"Parent page '{database_name}' not found.")
            return False

        if self._get_table(table_name):
            _LOGGER.debug(f"Table '{table_name}' already exists.")
            return True

        return bool(self._create_table(parent_page_id, table_name, model))

    def _create_table(
        self,
        parent_page_id: str,
        table_name: str,
        model: Type[BaseModelWithUpdatedAt],
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

    def get_last_entry_date(
        self,
        database_name: str,
        table_name: str,
        model: Type[BaseModelWithUpdatedAt],
    ) -> Optional[datetime]:
        updated_at_field = "updated_at"
        table = self._get_table(table_name)
        if not table:
            raise ValueError(
                f"Table '{table_name}' not found in database '{database_name}'"
            )

        response = self._client.databases.query(
            database_id=table.get("id"),
            sorts=[{"property": updated_at_field, "direction": "descending"}],
            page_size=1,
        )

        results = response.get("results", [])

        if not results:
            _LOGGER.info(f"No entries found in table '{table_name}'.")
            return None  # Return None if no entries are found

        last_entry = results[0]
        notion_date = (
            last_entry["properties"]
            .get(updated_at_field, {})
            .get("date", {})
            .get("start")
        )

        if not notion_date:
            _LOGGER.warning(
                f"Updated_at field '{updated_at_field}' not found "
                f"in the last entry."
            )
            return None

        return datetime.fromisoformat(notion_date)

    def save_entry(
        self, database_name: str, table_name: str, data: BaseModelWithUpdatedAt
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
