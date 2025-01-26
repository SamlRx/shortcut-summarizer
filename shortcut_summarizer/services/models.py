from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar("T")
V = TypeVar("V")


class Step(ABC):
    @abstractmethod
    def __call__(self, data: T) -> V:
        pass


class InitStep(ABC):
    @abstractmethod
    def __call__(self) -> V:
        pass


class SinkStep(ABC):
    @abstractmethod
    def __call__(self, data: T) -> None:
        pass
