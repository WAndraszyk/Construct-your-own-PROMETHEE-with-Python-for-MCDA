import pandas as pd

from math import ceil, floor
from typing import List, Tuple, Dict
from core.aliases import NumericValue


class SRFWeights:
    """
    This module computes weights of criteria using the revised Simos (or Simos-Roy-Figueira; SRF) method.
    """

    def __init__(self, criteria_ranks: pd.Series, criteria_weight_ratio: NumericValue,
                 decimal_place: int = 2):
        """
        :param criteria_ranks: Series with ranks of criteria. Ranks can be the same for the same weight.
                              Gaps between ranks indicate amount of white cards between criteria.
                              Smallest rank indicates the lowest weight and has to be 1
        :param criteria_weight_ratio: Difference between the least important criterion and the most important criterion.
        :param decimal_place: Number of decimal places for returned weights.
        """
        self.criteria_ranks = criteria_ranks
        self.criteria_weight_ratio = criteria_weight_ratio
        self.decimal_place = decimal_place

    def __calculate_spaces_between_criteria_ranks(self) -> pd.Series:
        """
        Calculate amount of spaces between criteria ranks.
        :return: Series with amount of spaces between criteria ranks
        """
        spaces_between_criteria_ranks = pd.Series(dtype=int)

        sorted_criteria_ranks = self.criteria_ranks.sort_values()

        for i, (criterion, rank) in enumerate(sorted_criteria_ranks[:-1].items()):
            spaces_between_criteria_ranks[criterion] = rank - sorted_criteria_ranks[i + 1]

        return spaces_between_criteria_ranks

    def __calculate_non_normalized_weights(self, spaces_between_criteria_ranks: pd.Series) -> pd.Series:
        """
        Calculate non-normalized weights of criteria.
        :param spaces_between_criteria_ranks: Series with amount of spaces between criteria ranks
        :return: Series with non-normalized weights of criteria
        """
        non_normalized_weights = pd.Series(dtype=float)

        ranks_without_white_cards = pd.Series()
        for i, (criterion, rank) in enumerate(self.criteria_ranks.sort_values().items()):
            ranks_without_white_cards[criterion] = rank - sum((spaces_between_criteria_ranks - 1)[:i])

        for i, (criterion, rank) in enumerate(ranks_without_white_cards.items()):
            non_normalized_weights[criterion] = 1 + (self.criteria_weight_ratio - 1) \
                                                * sum(spaces_between_criteria_ranks[:i]) / \
                                                sum(spaces_between_criteria_ranks)

        return non_normalized_weights

    @staticmethod
    def __normalize_weight_up_to_100(non_normalized_weights: pd.Series) -> pd.Series:
        """
        Normalize weights of criteria up to 100.
        :param non_normalized_weights: Series with non-normalized weights of criteria
        :return: Series with normalized weights of criteria
        """
        sum_of_weights = sum(non_normalized_weights)
        return non_normalized_weights / sum_of_weights * 100

    def __truncate_normalized_weights(self, normalized_weights: pd.Series) -> pd.Series:
        """
        Truncate normalized weights of criteria to self.decimal_place number of figures after the decimal point.
        :param normalized_weights: List with normalized weights of criteria
        :return: Series with truncated weights of criteria
        """

        return normalized_weights.map(lambda weight:
                                      max(floor(10 ** self.decimal_place * weight) /
                                          10 ** self.decimal_place, 10 ** -self.decimal_place))

    def __calculate_correction_ratios(self, normalized_weights: pd.Series,
                                      truncated_weights: pd.Series
                                      ) -> pd.DataFrame:
        """
        Calculate positive and negative ratios for final rounding.
        :param normalized_weights: Series with normalized weights of criteria
        :param truncated_weights: Series with truncated weights of criteria
        :return: DataFrame with positive and negative ratios for final rounding
        """
        weights_df = pd.DataFrame({'normalized': normalized_weights, 'truncated': truncated_weights},
                                  index=normalized_weights.index)

        positive_ratios = weights_df.apply(lambda row: (10 ** -self.decimal_place -
                                                        (row['normalized'] - row['truncated'])) / row['normalized'],
                                           axis=1)

        negative_ratios = weights_df.apply(lambda row: (row['normalized'] - row['truncated']) / row['normalized'],
                                           axis=1)

        ratios = pd.DataFrame({'positive': positive_ratios, 'negative': negative_ratios},
                              index=normalized_weights.index)

        return ratios

    def __calculate_size_of_upward_rounded_set(self, truncated_weights: pd.Series) -> NumericValue:
        """
        Calculate size of upward rounded set.
        :param truncated_weights: List with truncated weights of criteria
        :return: Size of upward rounded set
        """
        return (100 - sum(truncated_weights)) * 10 ** self.decimal_place

    def __round_properly_weights(self, normalized_weights: pd.Series,
                                 truncated_weights: pd.Series,
                                 ) -> pd.Series:
        """
        Round weights with special algorithm to avoid rounding errors.
        :param normalized_weights: Series with normalized weights of criteria
        :param truncated_weights: Series with truncated weights of criteria
        :return: Series with rounded weights of criteria, sorted by order of passed criteria
        """
        ratios = self.__calculate_correction_ratios(normalized_weights, truncated_weights)

        positive_ratios_larger_than_negative_ratios = ratios[ratios['positive'] > ratios['negative']].index

        size_of_upward_rounded_set = int(self.__calculate_size_of_upward_rounded_set(truncated_weights))

        positive_ratios = ratios['positive'].sort_values(ascending=False)
        negative_ratios = ratios['negative'].sort_values(ascending=False)

        n_criteria = len(self.criteria_ranks)

        if size_of_upward_rounded_set + len(positive_ratios_larger_than_negative_ratios) <= n_criteria:

            round_downward_list = positive_ratios_larger_than_negative_ratios
            to_add_to_downward_list = n_criteria - size_of_upward_rounded_set \
                                      - len(positive_ratios_larger_than_negative_ratios)

            if to_add_to_downward_list > 0:
                for criterion in negative_ratios.index:
                    if criterion not in positive_ratios_larger_than_negative_ratios:
                        round_downward_list.append(criterion)
                        to_add_to_downward_list -= 1
                        if to_add_to_downward_list == 0:
                            break

        else:
            round_downward_list = []
            to_add_to_downward_list = n_criteria - size_of_upward_rounded_set

            if to_add_to_downward_list > 0:
                for criterion in positive_ratios.index:
                    if criterion not in positive_ratios_larger_than_negative_ratios:
                        round_downward_list.append(criterion)
                        to_add_to_downward_list -= 1
                        if to_add_to_downward_list == 0:
                            break

        round_upward_list = list(set(self.criteria_ranks.index).difference(set(round_downward_list)))

        base = 10 ** self.decimal_place

        rounded_downward = normalized_weights[normalized_weights.index.isin(round_downward_list)].map(
            lambda weight: floor(weight * base) / base)
        rounded_upward = normalized_weights[normalized_weights.index.isin(round_upward_list)].map(
            lambda weight: ceil(weight * base) / base)

        balanced_normalized_weights = pd.concat([rounded_downward, rounded_upward]).reindex(self.criteria_ranks.index)

        return balanced_normalized_weights

    def calculate_srf_weights(self) -> pd.Series:
        """
        Calculate weights of criteria with SRF method.
        :return: Series with weights of criteria
        """
        spaces_between_criteria_ranks = self.__calculate_spaces_between_criteria_ranks()
        non_normalized_weights = self.__calculate_non_normalized_weights(spaces_between_criteria_ranks)
        normalized_weights = self.__normalize_weight_up_to_100(non_normalized_weights)
        truncated_weights = self.__truncate_normalized_weights(normalized_weights)
        balanced_normalized_weights = self.__round_properly_weights(normalized_weights, truncated_weights)

        return balanced_normalized_weights
