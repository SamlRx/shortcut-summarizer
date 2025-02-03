from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel


class ReportPort(ABC):

    @abstractmethod
    def init_table(
        self, database_name: str, table_name: str, model: BaseModel.__class__
    ) -> bool:
        pass

    @abstractmethod
    def save_entry(
        self, database_name: str, table_name: str, data: BaseModel
    ) -> None:
        pass

    @abstractmethod
    def get_last_entry_date(self) -> datetime:
        pass
