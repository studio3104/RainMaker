from typing import List, Union

import pandas
import numpy
import math

from ._abc import SupportResistance


class WindowShifting(SupportResistance):
    # Ref: https://medium.datadriveninvestor.com/how-to-detect-support-resistance-levels-and-breakout-using-python-f8b5dac42f21

    def __init__(self, df: pandas.DataFrame) -> None:
        self.window_size = math.ceil(len(df) / 7)
        print(self.window_size)
        super().__init__(df)

    def _set_levels(self) -> None:
        self._mean = numpy.mean(self.df['High'] - self.df['Low'])
        high_range = self._determine_max_or_min_within_window('High', max)
        low_range = self._determine_max_or_min_within_window('Low', min)

        pivot = math.ceil(self.window_size / 2)
        self.__set_levels(high_range, pivot, self._resistances)
        self.__set_levels(low_range, pivot, self._supports)

    def __set_levels(self, nums: List[int], pivot: int, target: List[int]) -> None:
        previous, counter = None, 0
        for n in nums:
            if n != previous:
                previous, counter = n, 1
                continue

            counter += 1
            if counter != pivot:
                continue

            target.append(n)
            if self._is_far_from_level(n):
                self._levels.append(n)

    def _is_far_from_level(self, level: int) -> bool:
        return numpy.sum([abs(level - x) < self._mean for x in self._levels]) == 0

    def _determine_max_or_min_within_window(self, high_or_low: str, max_or_min: Union[max, min]) -> List[int]:
        nums = numpy.array(self.df[high_or_low])
        n = len(nums)
        k = self.window_size
        if n * k == 0:
            return []

        left, right = [0] * n, [0] * n
        left[0], right[n - 1] = nums[0], nums[n - 1]

        for i in range(1, n):
            j = n - i - 1
            left[i] = nums[i] if i % k == 0 else max_or_min(left[i - 1], nums[i])
            right[j] = nums[j] if (j + 1) % k == 0 else max_or_min(right[j + 1], nums[j])

        return [int(max_or_min(left[i + k - 1], right[i])) for i in range(n - k + 1)]
