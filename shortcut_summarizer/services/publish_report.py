from typing import List

from domains.models import TicketReport
from functional import seq
from ports.report import ReportPort
from services.models import SinkStep


class PublishTicketReports(SinkStep):
    def __init__(self, report_repository: ReportPort) -> None:
        self._report_repository = report_repository

    def __call__(self, data: List[TicketReport]) -> None:
        self._report_repository.save_report(self._ticket_reports_to_dict(data))

    @staticmethod
    def _ticket_reports_to_dict(
        ticket_reports: List[TicketReport],
    ) -> List[dict]:
        return seq(ticket_reports).map(lambda x: x.to_dict()).to_list()
