"""
    This module computes weights of criteria using the revised Simos (or Simos-Roy-Figueira; SRF) method.
"""
import pandas as pd

from math import ceil, floor
from core.aliases import NumericValue

__all__ = ['calculate_srf_weights']


def _calculate_spaces_between_criteria_ranks(criteria_ranks: pd.Series) -> pd.Series:
    """
    Calculate amount of spaces between criteria ranks.
    :return: Series with amount of spaces between criteria ranks
    """
    spaces_between_criteria_ranks = pd.Series(dtype=int)

    sorted_criteria_ranks = criteria_ranks.sort_values()

    for i, (criterion, rank) in enumerate(sorted_criteria_ranks[:-1].items()):
        spaces_between_criteria_ranks[criterion] = rank - sorted_criteria_ranks[i + 1]

    return spaces_between_criteria_ranks


def _calculate_non_normalized_weights(criteria_ranks: pd.Series,
                                      criteria_weight_ratio: NumericValue,
                                      spaces_between_criteria_ranks: pd.Series) -> pd.Series:
    """
    Calculate non-normalized weights of criteria.
    :param spaces_between_criteria_ranks: Series with amount of spaces between criteria ranks
    :return: Series with non-normalized weights of criteria
    """
    non_normalized_weights = pd.Series(dtype=float)

    ranks_without_white_cards = pd.Series()
    for i, (criterion, rank) in enumerate(criteria_ranks.sort_values().items()):
        ranks_without_white_cards[criterion] = rank - sum((spaces_between_criteria_ranks - 1)[:i])

    for i, (criterion, rank) in enumerate(ranks_without_white_cards.items()):
        non_normalized_weights[criterion] = round(1 + (criteria_weight_ratio - 1)
                                                  * sum(spaces_between_criteria_ranks[:i]) /
                                                  sum(spaces_between_criteria_ranks), 2)

    return non_normalized_weights


def _normalize_weight_up_to_100(non_normalized_weights: pd.Series) -> pd.Series:
    """
    Normalize weights of criteria up to 100.
    :param non_normalized_weights: Series with non-normalized weights of criteria
    :return: Series with normalized weights of criteria
    """
    sum_of_weights = sum(non_normalized_weights)
    return non_normalized_weights / sum_of_weights * 100


def _truncate_normalized_weights(normalized_weights: pd.Series,
                                 decimal_place: int) -> pd.Series:
    """
    Truncate normalized weights of criteria to self.decimal_place number of figures after the decimal point.
    :param normalized_weights: List with normalized weights of criteria
    :return: Series with truncated weights of criteria
    """

    return normalized_weights.map(lambda weight:
                                  max(floor(10 ** decimal_place * weight) /
                                      10 ** decimal_place, 10 ** -decimal_place))


def _calculate_correction_ratios(normalized_weights: pd.Series,
                                 truncated_weights: pd.Series,
                                 decimal_place: int
                                 ) -> pd.DataFrame:
    """
    Calculate positive and negative ratios for final rounding.
    :param normalized_weights: Series with normalized weights of criteria
    :param truncated_weights: Series with truncated weights of criteria
    :return: DataFrame with positive and negative ratios for final rounding
    """
    weights_df = pd.DataFrame({'normalized': normalized_weights, 'truncated': truncated_weights},
                              index=normalized_weights.index)

    positive_ratios = weights_df.apply(lambda row: (10 ** - decimal_place -
                                                    (row['normalized'] - row['truncated'])) / row['normalized'],
                                       axis=1)

    negative_ratios = weights_df.apply(lambda row: (row['normalized'] - row['truncated']) / row['normalized'],
                                       axis=1)

    ratios = pd.DataFrame({'positive': positive_ratios, 'negative': negative_ratios},
                          index=normalized_weights.index)

    return ratios


def _calculate_size_of_upward_rounded_set(truncated_weights: pd.Series,
                                          decimal_place: int) -> NumericValue:
    """
    Calculate size of upward rounded set.
    :param truncated_weights: List with truncated weights of criteria
    :return: Size of upward rounded set
    """
    return (100 - sum(truncated_weights)) * 10 ** decimal_place


def _round_properly_weights(criteria_ranks: pd.Series,
                            normalized_weights: pd.Series,
                            truncated_weights: pd.Series,
                            decimal_place: int
                            ) -> pd.Series:
    """
    Round weights with special algorithm to avoid rounding errors.
    :param normalized_weights: Series with normalized weights of criteria
    :param truncated_weights: Series with truncated weights of criteria
    :return: Series with rounded weights of criteria, sorted by order of passed criteria
    """
    ratios = _calculate_correction_ratios(normalized_weights, truncated_weights, decimal_place)

    positive_ratios_larger_than_negative_ratios = ratios[ratios['positive'] > ratios['negative']].index

    size_of_upward_rounded_set = int(_calculate_size_of_upward_rounded_set(truncated_weights, decimal_place))

    positive_ratios = ratios['positive'].sort_values(ascending=False)
    negative_ratios = ratios['negative'].sort_values(ascending=True)

    n_criteria = len(criteria_ranks)

    if size_of_upward_rounded_set + len(positive_ratios_larger_than_negative_ratios) <= n_criteria:

        round_downward_list = positive_ratios_larger_than_negative_ratios
        to_add_to_downward_list = n_criteria - size_of_upward_rounded_set - len(
            positive_ratios_larger_than_negative_ratios)

        if to_add_to_downward_list > 0:
            for criterion in negative_ratios.index:
                if criterion not in positive_ratios_larger_than_negative_ratios:
                    round_downward_list = round_downward_list.append(pd.Index([criterion]))
                    to_add_to_downward_list -= 1
                    if to_add_to_downward_list == 0:
                        break

    else:
        round_downward_list = []
        to_add_to_downward_list = n_criteria - size_of_upward_rounded_set

        if to_add_to_downward_list > 0:
            for criterion in positive_ratios.index:
                if criterion not in positive_ratios_larger_than_negative_ratios:
                    round_downward_list = round_downward_list.append(pd.Index([criterion]))
                    to_add_to_downward_list -= 1
                    if to_add_to_downward_list == 0:
                        break

    round_upward_list = list(set(criteria_ranks.index).difference(set(round_downward_list)))

    base = 10 ** decimal_place

    rounded_downward = normalized_weights[normalized_weights.index.isin(round_downward_list)].map(
        lambda weight: floor(weight * base) / base)
    rounded_upward = normalized_weights[normalized_weights.index.isin(round_upward_list)].map(
        lambda weight: ceil(weight * base) / base)

    balanced_normalized_weights = pd.concat([rounded_downward, rounded_upward]).reindex(criteria_ranks.index)

    return balanced_normalized_weights


def calculate_srf_weights(criteria_ranks: pd.Series, criteria_weight_ratio: NumericValue,
                          decimal_place: int = 2) -> pd.Series:
    """
    Calculate weights of criteria with SRF method.
    :return: Series with weights of criteria
    """

    primal_index = criteria_ranks.index

    spaces_between_criteria_ranks = _calculate_spaces_between_criteria_ranks(criteria_ranks)
    non_normalized_weights = _calculate_non_normalized_weights(criteria_ranks, criteria_weight_ratio,
                                                               spaces_between_criteria_ranks)
    normalized_weights = _normalize_weight_up_to_100(non_normalized_weights)
    truncated_weights = _truncate_normalized_weights(normalized_weights, decimal_place)
    balanced_normalized_weights = _round_properly_weights(normalized_weights, normalized_weights, truncated_weights,
                                                          decimal_place)

    return balanced_normalized_weights.reindex(primal_index)
