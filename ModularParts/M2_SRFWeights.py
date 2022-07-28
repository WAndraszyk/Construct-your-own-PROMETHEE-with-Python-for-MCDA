import numpy as np
from math import ceil, floor
from typing import List, Union
from core.aliases import NumericValue


class SurrogateWeights:
    """
    This module computes weights of criteria using the revised Simos (or Simos-Roy-Figueira; SRF) method.
    """

    def __init__(self, criteria_rank: List[Union[None, str, List[str]]], criteria_weight_ratio: NumericValue,
                 decimal_place: int = 2):
        """
        :param criteria_rank: List of criteria in proper order.
                              First criterion in list indicates the least important criterion.
                              User can group criteria by passing them in nested list to indicate
                              the same importance for them.
                              User can insert to list "White cards" (None's) to make difference between
                              separated criteria more substantial.
        :param criteria_weight_ratio: Difference between the least important criterion and the most important criterion.
        :param decimal_place: Number of decimal places for returned weights.
        """
        self.decimal_place = decimal_place
        self.criteria_weight_ratio = criteria_weight_ratio
        self.criteria_rank = criteria_rank

    def __calculate_white_cards_between_criteria(self) -> List[int]:
        """
        Calculate amount of white cards between criteria.

        :return: List amount of white cards between criteria.
        """
        white_cards_between_criteria = []

        for i, criterion in enumerate(self.criteria_rank):
            if criterion is not None:
                n_white_cards = 0
                for next_criterion in self.criteria_rank[i + 1:]:
                    if next_criterion is None:
                        n_white_cards += 1
                    else:
                        break
                white_cards_between_criteria.append(n_white_cards)

        return white_cards_between_criteria

    def __calculate_not_normalized_weights(self, white_cards_between_criteria) -> List[float]:
        """
        Calculate not normalized weights for every criterion.

        :return: List of not normalized weights.
        """
        criteria_rank_with_out_white_cards = [criterion for criterion in self.criteria_rank if criterion is not None]

        v = len(criteria_rank_with_out_white_cards) - 1

        not_normalized_weights = []

        for i, criterion in enumerate(criteria_rank_with_out_white_cards):
            weight = 1 + ((self.criteria_weight_ratio - 1) *
                          (i - 1 + np.sum(white_cards_between_criteria[:i])) /
                          (v - 1 + np.sum(white_cards_between_criteria[:v])))
            if criterion is list:
                not_normalized_weights += [weight for _ in criterion]
            else:
                not_normalized_weights.append(weight)

        return not_normalized_weights

    def __normalize_weights(self, not_normalized_weights) -> List[float]:
        """
        Normalize weights passed as argument.

        :return: List of normalized weights. Weights sum up to 100.
        """
        normalized_weights = []

        sum_of_weights = np.sum(not_normalized_weights)

        precise_rounding_factor = 10 ** self.decimal_place  # It allows for more precise rounding

        not_normalized_weights = not_normalized_weights * 100 * precise_rounding_factor

        for not_normalized_weight in not_normalized_weights[:len(not_normalized_weights) // 2]:
            normalized_weights.append(round(ceil(not_normalized_weight / sum_of_weights) /
                                            precise_rounding_factor, self.decimal_place))

        for not_normalized_weight in not_normalized_weights[len(not_normalized_weights) // 2:]:
            normalized_weights.append(round(floor(not_normalized_weight / sum_of_weights) /
                                            precise_rounding_factor, self.decimal_place))

        return normalized_weights

    def srf_weights(self) -> List[float]:
        """
        Calculate normalized weights for criteria_rank and criteria_weight_ratio passed to class.

        :return: List of normalized weights. Weights sum up to 100.
        """
        white_cards = self.__calculate_white_cards_between_criteria()
        not_normalized_weights = self.__calculate_not_normalized_weights(white_cards)
        normalized_weights = self.__normalize_weights(not_normalized_weights)

        return normalized_weights
