from datetime import datetime

from notion_client import Client

from shortcut_summarizer.domains.report import TicketReport
from shortcut_summarizer.ports.report import ReportPort


class NotionRepository(ReportPort):

    def __init__(self, client: Client) -> None:
        self._client = client

    def create_database(
        self, parent_page_id: str, database_name: str, properties: dict
    ) -> dict:
        """
        Create a new database in Notion.

        :param parent_page_id: The ID of the Notion page where the database
        will be created.
        :param database_name: The title of the new database.
        :param properties: A dictionary defining the database p
        roperties (fields).
        :return: The response from the Notion API.
        """
        database = {
            "parent": {"type": "page_id", "page_id": parent_page_id},
            "title": [{"type": "text", "text": {"content": database_name}}],
            "properties": properties,
        }

        return self._client.databases.create(**database)

    def get_last_entry_date(self) -> datetime:
        return datetime.now()

    def save_report(self, report: TicketReport) -> None:
        pass
