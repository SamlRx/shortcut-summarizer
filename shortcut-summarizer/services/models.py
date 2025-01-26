from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar('T')
V = TypeVar('V')

class Step(ABC):

    @abstractmethod
    def execute(self, data: T) -> V:
        pass

class InitStep(ABC):

    @abstractmethod
    def execute(self) -> V:
        pass

