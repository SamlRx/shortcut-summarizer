from datetime import datetime
from enum import Enum

import pytest
from pydantic import BaseModel

from shortcut_summarizer.repository.notion import NotionSchemaConverter


class TestEnum(Enum):
    OPTION_A = "Option A"
    OPTION_B = "Option B"

class TestModel(BaseModel):
    name: str
    age: int
    height: float
    birthday: datetime
    category: TestEnum

def test_schema_conversion():
    # Given a Pydantic model with various field types
    expected_schema = {
        "name": {"type": "rich_text"},
        "age": {"type": "number"},
        "height": {"type": "number"},
        "birthday": {"type": "date"},
        "category": {
            "type": "select",
            "select": {
                "options": [
                    {"name": "Option A", "color": "default"},
                    {"name": "Option B", "color": "default"}
                ]
            }
        }
    }

    # When converting the model to a Notion schema
    schema = NotionSchemaConverter().to_notion_schema(TestModel)

    # Then the generated schema should match the expected structure
    assert schema == expected_schema