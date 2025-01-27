from abc import ABC, abstractmethod
from datetime import datetime

from shortcut_summarizer.domains.report import TicketReport


class ReportPort(ABC):

    @abstractmethod
    def save_report(self, report: TicketReport) -> None:
        pass

    @abstractmethod
    def get_last_entry_date(self) -> datetime:
        pass