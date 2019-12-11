import math
from typing import List
import scipy.stats as stats

import numpy.random as np

# TODO Implement the methods for each distribution implementation
# This includes the operands: | < > <= >= == &
class Distribution(object):

    def __gt__(self, other):
        return 1 - self.__le__(other)

    def __lt__(self, other):
        return self.__le__(other) - self.__eq__(other)

    def __ge__(self, other):
        return 1 - self.__lt__(other)

    def __eq__(self, value):
        raise NotImplementedError()

    def __le__(self, other):
        raise NotImplementedError()

    def __radd__(self, other):
        raise NotImplementedError()

    def __contains__(self, item):
        raise NotImplementedError()



class Discrete(Distribution):

    def __init__(self, init_list=None):
        self.dist_list = {}
        self.total = 0
        if init_list is not None:
            self.dist_list = init_list

    def append(self, data):
        if data not in self.dist_list:
            self.dist_list[data] = 0
        self.total += 1
        self.dist_list[data] += 1

    def __eq__(self, other):
        if other not in self.dist_list:
            return 0
        return self.dist_list[other] / self.total

    def __le__(self, other):
        raise NotImplementedError()

    def __str__(self):
        return str(self.dist_list)


class Gaussian(Distribution):

    def __init__(self, mean, variance, CI = 0.85):
        self.mean = mean
        self.variance = variance
        self.CI = CI
        self.dist = stats.norm(loc=mean, scale=variance)

    def __call__(self, *args, **kwargs):
        return self.dist.rvs()

    def __eq__(self, other):
        if isinstance(other, (int, float)):
            return self.dist.pdf(other)

    def __le__(self, other):
        if isinstance(other, (int, float)):
            return self.dist.cdf(other)

    def __str__(self):
        return str("Mean: " + str(self.mean) + " Variance: " + str(self.variance))



class DataPointList(object):
    def __init__(self, names):
        self.names = names
        self.data = []
        self.mean_variance = {}
        for name in self.names:
            self.mean_variance[name] = [0, 0]


    def append(self, row):
        n = len(self.data)
        self.data.append(row)
        for key, value in row.items():
            prev_mu = self.mean_variance[key][0]
            self.mean_variance[key][0] = (n * prev_mu + value) / (n + 1)
            if n > 0:
                self.mean_variance[key][1] = ((n - 1) * self.mean_variance[key][1]) / n + (n * ((prev_mu - value) ** 2))/((n + 1) * n)
            else:
                self.mean_variance[key][1] = 0

    def __contains__(self, item):
        return item in self.names

    def __call__(self, *args, **kwargs):
        func = args[0]
        new_data = DataPointList(self.names)
        for point in self.data:
            if func(point):
                new_data.append(point)
        return new_data

    def __len__(self):
        return len(self.data)

    # def mean_variance(self, name):
    #     total = len(self)
    #     count = 0
    #     for point in self.data:
    #         count += point[name]
    #     mean = count / total
    #     count = 0
    #     for point in self.data:
    #         count += (point[name] - mean) * (point[name] - mean)
    #     return mean, count / total

    def ci(self, name, percent):
        z = stats.zscore([percent])[0]
        c = z * (math.sqrt(self.mean_variance[name][1]) / math.sqrt(len(self.data)))
        return self.mean_variance[name][0] - c, self.mean_variance[name][0] + c

