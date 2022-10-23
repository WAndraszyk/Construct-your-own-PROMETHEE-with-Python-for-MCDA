from pandas import Series

from core.aliases import NumericValue, RankedCriteria
from typing import List
from core.preference_commons import criteria_series
import pandas as pd


__all__ = []

class SurrogateWeights:
    """This class computes weights of criteria. It requires the user to specify the
    criteria ranking. In this ranking each criterion is associated with a unique position.
    The ranking should list the criteria from the most to least important."""

    def __init__(self, ranked_criteria: RankedCriteria,
                 decimal_place: NumericValue = 3):
        self.ranked_criteria = ranked_criteria
        self.decimal_place = decimal_place

    def __weight_order(self,
                       weights: List[NumericValue]) -> Series:
        """
        This method assigns weights to according criteria.

        :return: Criteria with weights
        """
        rank_summed = self.ranked_criteria.replace([i + 1 for i in range(len(weights))], weights)
        return rank_summed

    def equal_weights(self) -> pd.Series:
        """
        In this method all weights are computed with the same value and sum up to 1.

        :return: Criteria with weights
        """
        n = self.ranked_criteria.size
        weights = []
        wi = round(1 / n, self.decimal_place)
        for i in range(1, n + 1):
            weights.append(wi)
        return criteria_series(self.ranked_criteria.keys(), weights)

    def rank_sum(self) -> Series:
        """
        In this method the more important the criterion is, the greater its weight.

        :return: Criteria with weights
        """
        n = self.ranked_criteria.size
        weights = []
        for i in range(1, n + 1):
            weights.append(round(2 * (n + 1 - i) / (n * (n + 1)), self.decimal_place))
        return self.__weight_order(weights)

    def reciprocal_of_ranks(self) -> Series:
        """
        This method computes weights by dividing each reciprocal of rank by the sum of these
        reciprocals for all criteria.

        :return: Criteria with weights
        """
        n = self.ranked_criteria.size
        weights = []
        sigma = 0
        for j in range(1, n + 1):
            sigma += 1 / j
        for i in range(1, n + 1):
            weights.append(round((1 / i) / sigma, self.decimal_place))
        return self.__weight_order(weights)

    def rank_order_centroid(self) -> Series:
        """
        The weights in this method reflect the centroid of the simplex defined by ranking of
        the criteria.

        :return: Criteria with weights
        """
        n = self.ranked_criteria.size
        weights = []
        for j in range(1, n + 1):
            sigma = 0
            for i in range(j, n + 1):
                sigma += 1 / i
            wi = round((1 / n) * sigma, self.decimal_place)
            weights.append(wi)
        return self.__weight_order(weights)
