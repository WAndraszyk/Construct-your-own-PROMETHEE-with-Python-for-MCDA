"""
This module computes weights of criteria. It requires the user to specify the
criteria ranking. In this ranking each criterion is associated with a rank
which represents its importance.
The lowest and rank is 1, and it represents the highest importance.
"""
from core.aliases import NumericValue
from core.enums import SurrogateMethod
from typing import List
from core.preference_commons import criteria_series
from core.input_validation import surrogate_weights_validation
import pandas as pd

__all__ = ["surrogate_weights"]


def surrogate_weights(criteria_ranks: pd.Series, method: SurrogateMethod,
                      decimal_place: int = 3) -> pd.Series:
    """
    Calculates weights with chosen surrogate weights method.

    :param criteria_ranks: criteria with according ranks
    :param method: chosen method of calculating weights
    :param decimal_place: the decimal place of the output numbers
    :return: Criteria with weights
    """

    def _weight_order(rc: pd.Series, weights: List[NumericValue]
                      ) -> pd.Series:
        """
        This method assigns weights to according criteria.

        :param rc: criteria ranks
        :param weights: calculated weights

        :return: Criteria with weights
        """
        rank_summed = rc.replace([i + 1 for i in range(len(weights))],
                                 weights)
        return criteria_series(rank_summed.index, rank_summed.values)

    def equal_weights(rc: pd.Series, dp: NumericValue = 3) -> pd.Series:
        """
        In this method all weights are computed with the same value and sum
        up to 1.

        :param rc: criteria ranks
        :param dp: decimal place

        :return: Criteria with weights
        """
        n = rc.size
        weights = []
        wi = round(1 / n, dp)
        for i in range(1, n + 1):
            weights.append(wi)
        return criteria_series(rc.index, weights)

    def rank_sum(rc: pd.Series, dp: NumericValue = 3) -> pd.Series:
        """
        In this method the more important the criterion is, the greater
        its weight.

        :param rc: criteria ranks
        :param dp: decimal place

        :return: Criteria with weights
        """
        n = rc.size
        weights = []
        for i in range(1, n + 1):
            weights.append(round(2 * (n + 1 - i) / (n * (n + 1)), dp))
        return _weight_order(rc, weights)

    def reciprocal_of_ranks(rc: pd.Series, dp: NumericValue = 3) -> pd.Series:
        """
        This method computes weights by dividing each reciprocal of rank by
        the sum of these reciprocals for all criteria.

        :param rc: criteria ranks
        :param dp: decimal place

        :return: Criteria with weights
        """
        n = rc.size
        weights = []
        sigma = 0
        for j in range(1, n + 1):
            sigma += 1 / j
        for i in range(1, n + 1):
            weights.append(round((1 / i) / sigma, dp))
        return _weight_order(rc, weights)

    def rank_order_centroid(rc: pd.Series, dp: NumericValue = 3) -> pd.Series:
        """
        The weights in this method reflect the centroid of the simplex
        defined by ranking of the criteria.

        :param rc: criteria ranks
        :param dp: decimal place

        :return: Criteria with weights
        """
        n = rc.size
        weights = []
        for j in range(1, n + 1):
            sigma = 0
            for i in range(j, n + 1):
                sigma += 1 / i
            wi = round((1 / n) * sigma, dp)
            weights.append(wi)
        return _weight_order(rc, weights)

    surrogate_weights_validation(criteria_ranks, decimal_place)
    # choosing right method for calculations
    if method is SurrogateMethod.EW:
        return equal_weights(criteria_ranks, decimal_place)
    if method is SurrogateMethod.RS:
        return rank_sum(criteria_ranks, decimal_place)
    if method is SurrogateMethod.RR:
        return reciprocal_of_ranks(criteria_ranks, decimal_place)
    if method is SurrogateMethod.ROC:
        return rank_order_centroid(criteria_ranks, decimal_place)
    else:
        raise TypeError("Method should be a SurrogateMethod Enum.")
