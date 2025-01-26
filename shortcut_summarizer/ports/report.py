from abc import ABC, abstractmethod


class ReportPort(ABC):



    @abstractmethod
    def save_report(self, data):
        pass
