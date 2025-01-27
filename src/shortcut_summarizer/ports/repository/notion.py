from shortcut_summarizer.domains.report import TicketReport
from shortcut_summarizer.ports.report import ReportPort


class NotionRepository(ReportPort):
    def save_report(self, report: TicketReport) -> None:
        pass
