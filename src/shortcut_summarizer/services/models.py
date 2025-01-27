from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")
V = TypeVar("V")


class Step(ABC, Generic[T, V]):
    @abstractmethod
    def __call__(self, data: T) -> V:
        pass


class InitStep(ABC, Generic[V]):
    @abstractmethod
    def __call__(self) -> V:
        pass


class SinkStep(ABC, Generic[T]):
    @abstractmethod
    def __call__(self, data: T) -> None:
        pass
