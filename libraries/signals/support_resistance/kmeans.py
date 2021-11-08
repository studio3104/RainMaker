from typing import List

import numpy
from sklearn.cluster import KMeans as _KMeans
from kneed import KneeLocator

from ._abc import SupportResistance


class KMeans(SupportResistance):
    # Ref: https://towardsdatascience.com/using-k-means-clustering-to-create-support-and-resistance-b13fdeeba12
    # Ref: https://www.nbshare.io/notebook/190163492/How-To-Calculate-Stocks-Support-And-Resistance-Using-Clustering/

    def _set_levels(self) -> None:
        high_array = numpy.array(self.df['High'])
        low_array = numpy.array(self.df['Low'])

        k = self._determine_k(high_array)
        high = self._detect_levels(k, high_array)
        low = self._detect_levels(k, low_array)

        for i in range(k):
            self._resistances.append(max(int(high[i][0]), int(high[i][1])))
            self._supports.append(min(int(low[i][0]), int(low[i][1])))
        self._levels = self._resistances + self._supports

    @staticmethod
    def _detect_levels(k: int, nums: numpy.ndarray) -> List[List[numpy.int64]]:
        kmeans = _KMeans(n_clusters=k).fit(nums.reshape(-1, 1))
        clusters = kmeans.predict(nums.reshape(-1, 1))  # noqa

        min_and_max = []
        for i in range(k):
            min_and_max.append([-numpy.inf, numpy.inf])

        for i in range(len(nums)):
            c = clusters[i]
            if nums[i] > min_and_max[c][0]:
                min_and_max[c][0] = nums[i]
            if nums[i] < min_and_max[c][1]:
                min_and_max[c][1] = nums[i]

        return min_and_max

    @staticmethod
    def _determine_k(nums: numpy.ndarray) -> int:
        sum_of_squared_distances = []
        _k = range(1, 15)
        for k in _k:
            km = _KMeans(n_clusters=k)
            km = km.fit(nums.reshape(-1, 1))
            sum_of_squared_distances.append(km.inertia_)  # noqa

        kn = KneeLocator(_k, sum_of_squared_distances, S=1.0, curve='convex', direction='decreasing')

        return kn.knee
