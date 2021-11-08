import numpy

from ._abc import SupportResistance


class Fractal(SupportResistance):
    # Ref: https://towardsdatascience.com/detection-of-price-support-and-resistance-levels-in-python-baedc44c34c9
    # Ref: https://medium.datadriveninvestor.com/how-to-detect-support-resistance-levels-and-breakout-using-python-f8b5dac42f21

    def _set_levels(self) -> None:
        mean = numpy.mean(self.df['High'] - self.df['Low'])

        for i in range(2, self.df.shape[0] - 2):
            level = None

            if self._is_support(i):
                level = int(self.df['Low'][i])
                self._supports.append(level)
            elif self._is_resistance(i):
                level = int(self.df['High'][i])
                self._resistances.append(level)

            if level is not None and self._is_far_from_level(mean, level):
                self._levels.append(level)

    def _is_support(self, i: int) -> bool:
        return (
                self.df['Low'][i] < self.df['Low'][i - 1] < self.df['Low'][i - 2] and
                self.df['Low'][i] < self.df['Low'][i + 1] < self.df['Low'][i + 2]
        )

    def _is_resistance(self, i: int) -> bool:
        return (
                self.df['High'][i] > self.df['High'][i - 1] > self.df['High'][i - 2] and
                self.df['High'][i] > self.df['High'][i + 1] > self.df['High'][i + 2]
        )

    def _is_far_from_level(self, mean: numpy.float64, level: int) -> bool:
        return numpy.sum([abs(level - x) < mean for x in self._levels]) == 0
