from typing import List

import numpy

from ._abc import SupportResistance


class Fractal(SupportResistance):
    def _detect_levels(self) -> List[int]:
        if self._levels:
            return self._levels

        mean = numpy.mean(self.df['High'] - self.df['Low'])

        for i in range(2, self.df.shape[0] - 2):
            level = None
            if self.is_support(i):
                level = int(self.df['Low'][i])
            if self.is_resistance(i):
                level = int(self.df['High'][i])

            if level is not None and self.is_far_from_level(mean, level):
                self._levels.append(level)

        return self._levels

    def is_support(self, i: int) -> bool:
        return (
                self.df['Low'][i] < self.df['Low'][i - 1] < self.df['Low'][i - 2] and
                self.df['Low'][i] < self.df['Low'][i + 1] < self.df['Low'][i + 2]
        )

    def is_resistance(self, i: int) -> bool:
        return (
                self.df['High'][i] > self.df['High'][i - 1] > self.df['High'][i - 2] and
                self.df['High'][i] > self.df['High'][i + 1] > self.df['High'][i + 2]
        )

    def is_far_from_level(self, mean: numpy.float64, level: int,) -> bool:
        return numpy.sum([abs(level - x) < mean for x in self._levels]) == 0
