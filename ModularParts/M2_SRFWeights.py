from math import ceil, floor
from typing import List, Tuple, Dict
from core.aliases import NumericValue


class SRFWeights:
    """
    This module computes weights of criteria using the revised Simos (or Simos-Roy-Figueira; SRF) method.
    """

    def __init__(self, criteria: List[str],
                 criteria_rank: List[NumericValue], criteria_weight_ratio: NumericValue,
                 decimal_place: int = 2):
        """
        :param criteria: List of names of criteria (string only)
        :param criteria_rank: List with ranks of criteria. Ranks can be the same for the same weight. Gaps between ranks
                              indicate amount of white cards between criteria. Smallest rank indicates
                              the lowest weight and has to be 1
        :param criteria_weight_ratio: Difference between the least important criterion and the most important criterion.
        :param decimal_place: Number of decimal places for returned weights.
        """
        self.criteria = criteria
        self.sorted_criteria = [criterion for _, criterion in sorted(zip(criteria_rank, criteria))]
        self.decimal_place = decimal_place
        self.criteria_weight_ratio = criteria_weight_ratio
        self.criteria_rank = sorted(criteria_rank)

    def __calculate_white_cards_between_criteria(self) -> List[int]:
        """
        Calculate amount of white cards between criteria.

        :return: List amount of white cards between criteria.
        """
        white_cards_between_criteria = []
        for i, rank in enumerate(self.criteria_rank[:-1]):
            white_cards_between_criteria.append(max(self.criteria_rank[i + 1] - rank - 1, 0))

        return white_cards_between_criteria

    def __calculate_non_normalized_weights(self, white_cards_between_criteria: List[NumericValue])\
            -> List[NumericValue]:
        """
        Calculate non-normalized weights of criteria.

        :param white_cards_between_criteria: List amount of white cards between criteria.
        :return: List non-normalized weights of criteria
        """
        non_normalized_weights = []

        rank_without_white_cards = []
        for i, rank in enumerate(self.criteria_rank):
            rank_without_white_cards.append(rank - sum(white_cards_between_criteria[:i]))

        for i, rank in enumerate(rank_without_white_cards):
            weight = 1 + (self.criteria_weight_ratio - 1) * \
                     (rank - 1 + sum(white_cards_between_criteria[:i])) / (
                    rank_without_white_cards[-1] - 1 + sum(white_cards_between_criteria))
            non_normalized_weights.append(weight)

        return non_normalized_weights

    @staticmethod
    def __normalize_weight_up_to_100(non_normalized_weights: List[NumericValue]) -> List[NumericValue]:
        """
        Normalize weights of criteria up to 100.

        :param non_normalized_weights: List with non-normalized weights of criteria
        :return: List with normalized weights of criteria
        """
        sum_of_weights = sum(non_normalized_weights)
        return [100 * weight / sum_of_weights for weight in non_normalized_weights]

    def __truncate_normalized_weights(self, normalized_weights: List[NumericValue]) -> List[NumericValue]:
        """
        Truncate normalized weights of criteria to self.decimal_place number of figures after the decimal point.

        :param normalized_weights: List with normalized weights of criteria
        :return: List with truncated weights of criteria
        """
        return [max(floor(10 ** self.decimal_place * weight) / 10 ** self.decimal_place, 10 ** -self.decimal_place)
                for weight in normalized_weights]

    def __calculate_correction_ratios(self, normalized_weights: List[NumericValue],
                                      truncated_weights: List[NumericValue]
                                      ) -> Tuple[Dict[str, NumericValue], Dict[str, NumericValue]]:
        """
        Calculate positive and negative ratios for final rounding.

        :param normalized_weights: List with normalized weights of criteria
        :param truncated_weights: List with truncated weights of criteria
        :return: Tuple with positive and negative ratios as dicts with criteria names as keys and ratios as values
        """
        positive_ratios = {criterion: (10 ** -self.decimal_place - (normalized_weight - truncated_weight)) /
                           normalized_weight for criterion, normalized_weight, truncated_weight in
                           zip(self.sorted_criteria, normalized_weights, truncated_weights)}

        negative_ratios = {criterion: (normalized_weight - truncated_weight) /
                           normalized_weight for criterion, normalized_weight, truncated_weight in
                           zip(self.sorted_criteria, normalized_weights, truncated_weights)}

        return positive_ratios, negative_ratios

    def __calculate_size_of_upward_rounded_set(self, truncated_weights: List[NumericValue]) -> NumericValue:
        """
        Calculate size of upward rounded set.

        :param truncated_weights: List with truncated weights of criteria
        :return: Size of upward rounded set
        """
        return (100 - sum(truncated_weights)) * 10 ** self.decimal_place

    def __round_properly_weights(self, normalized_weights: List[NumericValue],
                                 truncated_weights: List[NumericValue]
                                 ) -> List[NumericValue]:
        """
        Round weights with special algorithm to avoid rounding errors.

        :param normalized_weights: List with normalized weights of criteria
        :param truncated_weights: List with truncated weights of criteria
        :return: List with rounded weights of criteria, sorted by order of passed criteria
        """
        positive_ratios, negative_ratios = self.__calculate_correction_ratios(normalized_weights, truncated_weights)

        positive_ratios_larger_than_negative_ratios = [criterion for criterion, positive_ratio, negative_ratio
                                                       in zip(self.sorted_criteria, positive_ratios.values(),
                                                              negative_ratios.values())
                                                       if positive_ratio > negative_ratio]

        size_of_upward_rounded_set = int(self.__calculate_size_of_upward_rounded_set(truncated_weights))

        positive_ratios = {k: v for k, v in sorted(positive_ratios.items(), key=lambda x: x[1])}
        negative_ratios = {k: v for k, v in sorted(negative_ratios.items(), key=lambda x: x[1], reverse=True)}

        n_criteria = len(self.criteria)

        if size_of_upward_rounded_set + len(positive_ratios_larger_than_negative_ratios) <= n_criteria:

            round_downward_list = positive_ratios_larger_than_negative_ratios
            to_add_to_downward_list = n_criteria - size_of_upward_rounded_set\
                                      - len(positive_ratios_larger_than_negative_ratios)

            if to_add_to_downward_list > 0:
                for criterion in list(negative_ratios.keys()):
                    if criterion not in positive_ratios_larger_than_negative_ratios:
                        round_downward_list.append(criterion)
                        to_add_to_downward_list -= 1
                        if to_add_to_downward_list == 0:
                            break

        else:
            round_downward_list = []
            to_add_to_downward_list = n_criteria - size_of_upward_rounded_set

            if to_add_to_downward_list > 0:
                for criterion in list(positive_ratios.keys())[::-1]:
                    if criterion not in positive_ratios_larger_than_negative_ratios:
                        round_downward_list.append(criterion)
                        to_add_to_downward_list -= 1
                        if to_add_to_downward_list == 0:
                            break

        round_upward_list = list(set(self.sorted_criteria).difference(set(round_downward_list)))

        round_downward_dict = {criterion: normalized_weights[self.sorted_criteria.index(criterion)] for
                               criterion in round_downward_list}
        round_upward_dict = {criterion: normalized_weights[self.sorted_criteria.index(criterion)] for
                             criterion in round_upward_list}

        base = 10 ** self.decimal_place
        rounded_criteria_and_weights = {}

        for d_criterion, d_weight in round_downward_dict.items():
            rounded_criteria_and_weights[d_criterion] = floor(d_weight * base) / base
        for u_criterion, u_weight in round_upward_dict.items():
            rounded_criteria_and_weights[u_criterion] = ceil(u_weight * base) / base

        sorted_criteria_weights = [rounded_criteria_and_weights[criterion] for criterion in self.criteria]

        return sorted_criteria_weights

    def calculate_srf_weights(self):
        """
        Calculate weights of criteria with SRF method.

        :return: List with weights of criteria, sorted by order of passed criteria
        """
        white_cards_between_criteria = self.__calculate_white_cards_between_criteria()
        non_normalized_weights = self.__calculate_non_normalized_weights(white_cards_between_criteria)
        normalized_weights = self.__normalize_weight_up_to_100(non_normalized_weights)
        truncated_weights = self.__truncate_normalized_weights(normalized_weights)
        criteria_weights = self.__round_properly_weights(normalized_weights, truncated_weights)

        return criteria_weights
