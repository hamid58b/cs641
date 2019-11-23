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

    def __eq__(self, other):
        if isinstance(other, (int, float)):
            return self.dist.pdf(other)

    def __le__(self, other):
        if isinstance(other, (int, float)):
            return self.dist.cdf(other)

    def __str__(self):
        return str("Mean: " + str(self.mean) + " Variance: " + str(self.variance))
