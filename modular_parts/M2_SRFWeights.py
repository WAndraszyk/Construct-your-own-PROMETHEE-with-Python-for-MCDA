"""
    .. image:: prometheePUT_figures/M2.jpg

    This module computes weights of criteria using the revised Simos
    (or Simos-Roy-Figueira; SRF) method.

    Implementation and naming of conventions are taken from
    :cite:p:`FigueiraRoy2001`.
"""
import math
from math import ceil, floor
from typing import cast

import pandas as pd

from core.input_validation.weights import srf_weights_validation

__all__ = ["calculate_srf_weights"]


def _calculate_spaces_between_criteria_ranks(
    criteria_ranks: pd.Series,
) -> pd.Series:
    """
    Calculate amount of spaces between criteria ranks.

    :param criteria_ranks: pd.Series with criteria as index and ranks as
                           values
    :return: pd.Series with all criteria but last as index and amount of
             spaces between criteria ranks as values
    """
    spaces_between_criteria_ranks = pd.Series(dtype=int)

    sorted_criteria_ranks = criteria_ranks.sort_values()

    # Calculate amount of spaces between criteria ranks by subtracting
    # the next pairs of ranks
    for i, (criterion, rank) in enumerate(sorted_criteria_ranks[:-1].items()):
        spaces_between_criteria_ranks[criterion] = sorted_criteria_ranks[i + 1] - rank

    return spaces_between_criteria_ranks


def _calculate_non_normalized_weights(
    criteria_ranks: pd.Series,
    criteria_weight_ratio: float,
    spaces_between_criteria_ranks: pd.Series,
) -> pd.Series:
    """
    Calculate non-normalized weights of criteria.

    :param criteria_ranks: pd.Series with criteria as index and ranks as
                           values
    :param criteria_weight_ratio: float, the ratio of
                the weight of the most important criterion to the weight of
                the least important criterion
    :param spaces_between_criteria_ranks: pd.Series with all criteria but
        last as index and amount of spaces between criteria ranks as values
    :return: pd.Series with criteria as index and non-normalized weights
             as values
    """
    non_normalized_weights = pd.Series(dtype=float)

    # Calculate cumulative sum of ranks (+1 for position)
    cumulative_ranks = pd.Series(dtype=float)
    for i, (criterion, rank) in enumerate(criteria_ranks.sort_values().items()):
        cumulative_ranks[criterion] = rank + sum(
            (spaces_between_criteria_ranks + 1)[:i]
        )

    # Calculate non-normalized weights
    for i, (criterion, rank) in enumerate(cumulative_ranks.items()):
        non_normalized_weights[criterion] = round(
            1
            + (criteria_weight_ratio - 1)
            * sum(spaces_between_criteria_ranks[:i])
            / sum(spaces_between_criteria_ranks),
            2,
        )

    return non_normalized_weights


def _normalize_weight_up_to_100(
    non_normalized_weights: pd.Series,
) -> pd.Series:
    """
    Normalize weights of criteria up to 100.

    :param non_normalized_weights: Series with non-normalized weights of
                                   criteria
    :return: Series with normalized weights of criteria
    """
    sum_of_weights = sum(non_normalized_weights)
    return non_normalized_weights / sum_of_weights * 100


def _truncate_normalized_weights(
    normalized_weights: pd.Series, decimal_place: int
) -> pd.Series:
    """
    Truncate normalized weights of criteria to self.decimal_place number
    of figures after the decimal point.

    :param normalized_weights: pd.Series with criteria as index and
                               normalized weights as values
    :param decimal_place: integer, the decimal place of the output weights
    :return: pd.Series with criteria as index and truncated weights as
             values
    """

    return normalized_weights.map(
        lambda weight: max(
            floor(10**decimal_place * weight) / 10**decimal_place,
            10**-decimal_place,
        )
    )


def _calculate_correction_ratios(
    normalized_weights: pd.Series,
    truncated_weights: pd.Series,
    decimal_place: int,
) -> pd.DataFrame:
    """
    Calculate positive and negative ratios for final rounding.
    Helps in deciding whether to round up or down.

    :param normalized_weights: pd.Series with criteria as index and
                               normalized weights as values
    :param truncated_weights: pd.Series with criteria as index and
                              truncated weights as values
    :param decimal_place: integer, the decimal place of the output weights
    :return: pd.DataFrame with criteria as index and 'positive' and 'negative'
             columns
    """

    # Init Dataframe for easier calculations
    weights_df = pd.DataFrame(
        {"normalized": normalized_weights, "truncated": truncated_weights},
        index=normalized_weights.index,
    )

    positive_ratios = weights_df.apply(
        lambda row: (10**-decimal_place - (row["normalized"] - row["truncated"]))
        / row["normalized"],
        axis=1,
    )

    negative_ratios = weights_df.apply(
        lambda row: (row["normalized"] - row["truncated"]) / row["normalized"],
        axis=1,
    )

    # Create DataFrame with positive and negative ratios
    ratios = pd.DataFrame(
        {"positive": positive_ratios, "negative": negative_ratios},
        index=normalized_weights.index,
    )

    return ratios


def _calculate_size_of_upward_rounded_set(
    truncated_weights: pd.Series, decimal_place: int
) -> int:
    """
    Calculate size of upward rounded set.

    :param truncated_weights: Series with criteria as index and
                              truncated weights as values
    :param decimal_place: int, the decimal place of the output numbers
    :return: int, size of upward rounded set
    """
    return int((100 - sum(truncated_weights)) * 10**decimal_place)


def _round_properly_weights(
    criteria_ranks: pd.Series,
    normalized_weights: pd.Series,
    truncated_weights: pd.Series,
    decimal_place: int,
) -> pd.Series:
    """
    Round weights with special algorithm to avoid rounding errors.
     See paper for details.

    :param criteria_ranks: pd.Series with criteria as index and ranks
                           as values
    :param normalized_weights: pd.Series with criteria as index and normalized
                               weights as values
    :param truncated_weights: pd.Series with criteria as index and truncated
                              weights as values
    :param decimal_place: integer, the decimal place of the output weights
    :return: pd.Series with criteria as index and
             properly rounded weights as values
    """

    # Calculate positive and negative ratios for final rounding
    ratios = _calculate_correction_ratios(
        normalized_weights, truncated_weights, decimal_place
    )

    # Get criteria where positive ratio is greater than negative ratio
    positive_ratios_larger_than_negative_ratios = ratios[
        ratios["positive"] > ratios["negative"]
    ].index

    # Calculate size of upward rounded set
    size_of_upward_rounded_set = _calculate_size_of_upward_rounded_set(
        truncated_weights, decimal_place
    )

    positive_ratios = ratios["positive"].sort_values(ascending=False)
    negative_ratios = ratios["negative"].sort_values(ascending=True)

    n_criteria = len(criteria_ranks)

    # Check which strategy to use (see paper for details)
    if (
        size_of_upward_rounded_set + len(positive_ratios_larger_than_negative_ratios)
        <= n_criteria
    ):

        round_downward_list = positive_ratios_larger_than_negative_ratios

        # Calculate size of downward rounded set
        to_add_to_downward_list = (
            n_criteria
            - size_of_upward_rounded_set
            - len(positive_ratios_larger_than_negative_ratios)
        )

        # Add criteria with the largest negative ratios to downward rounded
        # set if they have negative ratio larger than positive ratio
        if to_add_to_downward_list > 0:
            for criterion in negative_ratios.index:
                if criterion not in positive_ratios_larger_than_negative_ratios:
                    round_downward_list = round_downward_list.append(
                        pd.Index([criterion])
                    )
                    to_add_to_downward_list -= 1
                    if math.isclose(to_add_to_downward_list, 0):
                        break

    else:
        round_downward_list = pd.Index([])
        to_add_to_downward_list = n_criteria - size_of_upward_rounded_set

        # Add criteria with the largest positive ratios to downward rounded
        # set if they do not have positive ratio larger than negative ratio
        if to_add_to_downward_list > 0:
            for criterion in positive_ratios.index:
                if criterion not in positive_ratios_larger_than_negative_ratios:
                    round_downward_list = round_downward_list.append(criterion)
                    to_add_to_downward_list -= 1
                    if math.isclose(to_add_to_downward_list, 0):
                        break

    # Create list with criteria to round upward
    round_upward_list = list(
        set(criteria_ranks.index).difference(set(round_downward_list))
    )

    base = 10**decimal_place

    # Round downward weights
    rounded_downward = normalized_weights[
        normalized_weights.index.isin(round_downward_list)
    ].map(lambda weight: floor(weight * base) / base)

    # Round upward weights
    rounded_upward = normalized_weights[
        normalized_weights.index.isin(round_upward_list)
    ].map(lambda weight: ceil(weight * base) / base)

    # Create Series with all criteria
    balanced_normalized_weights = pd.concat([rounded_downward, rounded_upward]).reindex(
        criteria_ranks.index
    )

    return balanced_normalized_weights


def calculate_srf_weights(
    criteria_ranks: pd.Series,
    criteria_weight_ratio: float,
    decimal_place: int = 2,
) -> pd.Series:
    """
    Calculate weights of criteria with Simos-Roy-Figueira method.

    :param criteria_ranks: pd.Series with criteria as index and
                           ranks as values
    :param criteria_weight_ratio: float, the ratio of
                the weight of the most important criterion to the weight of
                the least important criterion
    :param decimal_place: integer, the decimal place of the output weights
    :return: pd.Series with criteria as index and weights as values
    """

    # Input validation
    srf_weights_validation(criteria_ranks, criteria_weight_ratio, decimal_place)

    # Save original index order
    original_index = criteria_ranks.index

    # Calculate 'White cards' between criteria
    spaces_between_criteria_ranks = _calculate_spaces_between_criteria_ranks(
        criteria_ranks
    )

    # Calculate non-normalized weights
    non_normalized_weights = _calculate_non_normalized_weights(
        criteria_ranks, criteria_weight_ratio, spaces_between_criteria_ranks
    )

    # Normalization of weights without consideration of the decimal place
    normalized_weights = _normalize_weight_up_to_100(non_normalized_weights)

    # Truncate weights to the decimal place (no rounding, just cut off)
    truncated_weights = _truncate_normalized_weights(normalized_weights, decimal_place)

    # Round weights with special algorithm to avoid rounding errors
    balanced_normalized_weights = _round_properly_weights(
        normalized_weights,
        normalized_weights,
        truncated_weights,
        decimal_place,
    )

    # Return weights with original index order
    return cast(pd.Series, balanced_normalized_weights.reindex(original_index))
