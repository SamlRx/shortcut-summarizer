from typing import List, Iterable


from streamable import Stream

from shortcut_summarizer.domains.report import TicketReport
from shortcut_summarizer.ports.report import ReportPort
from shortcut_summarizer.services.models import SinkStep


class PublishTicketReports(SinkStep):
    def __init__(self, report_repository: ReportPort) -> None:
        self._report_repository = report_repository

    def __call__(self, data: Iterable[TicketReport]) -> None:
        (
            Stream(data)
            .map(self._report_repository.save_report)
         )
