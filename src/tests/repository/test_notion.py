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


class MockEnum(Enum):
    OPTION_A = "Option A"
    OPTION_B = "Option B"


class MockModel(BaseModel):
    name: str
    age: int
    height: float
    birthday: datetime
    category: MockEnum


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
    schema = NotionSchemaConverter().to_notion_schema(MockModel)

    # Then the generated schema should match the expected structure
    assert schema == expected_schema


def test_schema_value_conversion() -> None:
    # Given a Pydantic model with various field types
    expected_payload: Dict = {
        "name": {"title": [{"text": {"content": "John Doe"}}]},
        "age": {"number": [{"content": 30}]},
        "height": {"number": [{"content": 1.75}]},
        "birthday": {"date": [{"content": "1990-01-01T00:00:00"}]},
        "category": {"select": {"name": "Option A"}},
    }
    mock_model = MockModel(
        name="John Doe",
        age=30,
        height=1.75,
        birthday=datetime(1990, 1, 1),
        category=MockEnum.OPTION_A,
    )

    # When converting the model to a Notion schema
    entry = NotionSchemaConverter().to_notion_entry(mock_model)

    # Then the generated schema should match the expected structure
    assert entry == expected_payload


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
                query="table",
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
    result = notion_repository.init_table("database", "table", MockModel)

    # Then it should create a new table and return True
    assert result is True
    mock_notion_client.databases.create.assert_called_once()


def test_save_entry(
    notion_repository: NotionRepository, mock_notion_client: MagicMock
) -> None:
    # Given a NotionRepository instance
    mock_notion_client.search.return_value = {
        "results": [{"id": "parent_page_123"}]
    }
    test_model = MockModel(
        name="John Doe",
        age=30,
        height=1.75,
        birthday=datetime(1990, 1, 1),
        category=MockEnum.OPTION_A,
    )

    # When saving an entry
    notion_repository.save_entry("database", "table", test_model)

    # Then it should save the entry to the table
    assert mock_notion_client.pages.create.call_count == 1
    assert mock_notion_client.pages.create.call_args.kwargs["properties"] == {
        "age": {"number": [{"content": 30}]},
        "birthday": {"date": [{"content": "1990-01-01T00:00:00"}]},
        "category": {"select": {"name": "Option A"}},
        "height": {"number": [{"content": 1.75}]},
        "name": {"title": [{"text": {"content": "John Doe"}}]},
    }
