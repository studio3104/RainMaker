from typing import List

from abc import ABC, abstractmethod

import pandas


class SupportResistance(ABC):
    def __init__(self, df: pandas.DataFrame) -> None:
        self.df = df
        self._levels: List[int] = []
        self._supports: List[int] = []
        self._resistances: List[int] = []
        self._set_levels()

    @property
    def levels(self) -> List[int]:
        return self._levels

    @property
    def supports(self) -> List[int]:
        return self._supports

    @property
    def resistances(self) -> List[int]:
        return self._resistances

    @abstractmethod
    def _set_levels(self) -> None:
        raise NotImplementedError
