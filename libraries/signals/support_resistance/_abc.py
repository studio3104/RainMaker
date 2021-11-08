from typing import List

from abc import ABC, abstractmethod

import pandas


class SupportResistance(ABC):
    _levels: List[int] = []

    def __init__(self, df: pandas.DataFrame) -> None:
        self.df = df
        self._detect_levels()

    @property
    def levels(self) -> List[int]:
        return self._levels

    @abstractmethod
    def _detect_levels(self) -> List[int]:
        raise NotImplementedError
