from datetime import datetime
from enum import Enum
from typing import Dict
from unittest.mock import MagicMock, call

import pytest
from notion_client import Client
from pydantic import BaseModel

from shortcut_summarizer.repository.notion import (
    NotionRepository,
    NotionSchemaConverter,
)


@pytest.fixture
def mock_notion_client() -> MagicMock:
    mock = MagicMock(spec=Client)
    mock.search = MagicMock()
    mock.databases = MagicMock()
    mock.pages = MagicMock()
    return mock


@pytest.fixture
def notion_repository(mock_notion_client: MagicMock) -> NotionRepository:
    return NotionRepository(mock_notion_client)


class TestEnum(Enum):
    OPTION_A = "Option A"
    OPTION_B = "Option B"


class TestModel(BaseModel):
    name: str
    age: int
    height: float
    birthday: datetime
    category: TestEnum


def test_schema_conversion() -> None:
    # Given a Pydantic model with various field types
    expected_schema: Dict = {
        "name": {"title": {}},
        "age": {"number": {}},
        "height": {"number": {}},
        "birthday": {"date": {}},
        "category": {
            "type": "select",
            "select": {
                "options": [
                    {"name": "Option A", "color": "default"},
                    {"name": "Option B", "color": "default"},
                ]
            },
        },
    }

    # When converting the model to a Notion schema
    schema = NotionSchemaConverter().to_notion_schema(TestModel)

    # Then the generated schema should match the expected structure
    assert schema == expected_schema


def test_init_table_table_exists(
    notion_repository: NotionRepository, mock_notion_client: MagicMock
) -> None:
    # Given a NotionRepository instance where the table already exists
    mock_notion_client.search.return_value = {
        "results": [{"id": "parent_page_123"}]
    }

    #  When initializing the table
    result = notion_repository.init_table("database", "table", MagicMock())

    # Then it should return True without creating a new table
    assert result is True
    mock_notion_client.search.assert_has_calls(
        [
            call(
                query="database",
                filter={"property": "object", "value": "page"},
            ),
            call(
                query="parent_page_123",
                filter={"property": "object", "value": "database"},
            ),
        ]
    )
    mock_notion_client.databases.create.assert_not_called()
    mock_notion_client.pages.create.assert_not_called()


def test_init_table_creates_new_table(
    notion_repository: NotionRepository, mock_notion_client: MagicMock
) -> None:
    # Given a NotionRepository instance where the table does not exist
    mock_notion_client.search.side_effect = [
        {"results": [{"id": "parent_page_123"}]},
        {"results": []},
    ]

    # When initializing the table
    result = notion_repository.init_table("database", "table", TestModel)

    # Then it should create a new table and return True
    assert result is True
    mock_notion_client.databases.create.assert_called_once()
