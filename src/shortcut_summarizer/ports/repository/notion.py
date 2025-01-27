from datetime import datetime

from shortcut_summarizer.domains.report import TicketReport
from shortcut_summarizer.ports.report import ReportPort


class NotionRepository(ReportPort):
    def get_last_entry_date(self) -> datetime:
        return datetime.now()

    def save_report(self, report: TicketReport) -> None:
        pass
