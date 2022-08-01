from core.aliases import NumericValue
from typing import List
import numpy as np


class PrometheeIIIFlow:
    """
    This class computes Promethee III intervals and ranking based on positive and negative flows,
    and preferences.
    """

    def __init__(self, alternatives: List[str], positive_flow: List[NumericValue], negative_flow: List[NumericValue],
                 preferences: List[List[NumericValue]]):
        """
        :param alternatives: List of alternatives names (strings only)
        :param positive_flow: List of positive flow values
        :param negative_flow: List of negative flow values
        :param preferences: List of preference of every alternative over others
        """
        self.alternatives = alternatives
        self.preferences = preferences
        self.flow = np.subtract(positive_flow, negative_flow)

    def calculate_ranking(self, alpha: NumericValue):
        """
        Calculates intervals and outranking pairs:
        1st alternative in pair | relation between variants | 2nd alternative in pair.
        Relationship types:
        P - preferred
        I - indifferent

        :param alpha - parameter used in calculating intervals
        :return: Intervals; List of preference ranking pairs
        """
        if alpha <= 0:
            raise Exception("Alpha has to be greater than 0")
        intervals = self.__calculate_intervals__(alpha)
        pairs = []
        for num_a, alternative_a in enumerate(self.alternatives):
            for num_b, alternative_b in enumerate(self.alternatives):
                if intervals[0][num_a] > intervals[1][num_b]:
                    pairs.append([alternative_a, ' P ', alternative_b])
                elif intervals[0][num_a] <= intervals[1][num_b] \
                        and intervals[0][num_b] <= intervals[1][num_a]:
                    pairs.append([alternative_a, ' I ', alternative_b])
                else:
                    pairs.append([alternative_a, ' ? ', alternative_b])

        return intervals, pairs

    def __calculate_intervals__(self, alpha: NumericValue):
        """
        Calculates intervals used in alternatives comparison.

        :param alpha - parameter used in calculating intervals
        """
        sigmas = []
        n = len(self.alternatives)
        for i in range(n):
            sum = 0
            for j in range(n):
                sum += np.square(self.preferences[i][j] - self.preferences[j][i] - self.flow[i])
            sigma = np.sqrt((1 / n) * sum)
            sigmas.append(sigma)

        x = []
        y = []
        for i in range(len(self.alternatives)):
            xi = self.flow[i] - alpha * sigmas[i]
            x.append(xi)
            yi = self.flow[i] + alpha * sigmas[i]
            y.append(yi)

        return [x, y]
