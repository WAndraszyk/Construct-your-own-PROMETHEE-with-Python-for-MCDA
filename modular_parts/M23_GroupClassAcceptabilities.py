"""
    .. image:: prometheePUT_figures/M23.png

    This module calculates alternatives support (basic and uni-modal).
    In other words, it calculates for each alternative the percentage of
    votes assigned for each category and in uni-modal version makes
    it "more smooth" (it is not allowed to have a category which has
    fewer votes than categories next to it)

    Implementation and naming convention are taken from the
    :cite:p:`DamartDiasMousseau2007`.
"""
from typing import List, Tuple, cast

import pandas as pd

from core.input_validation.sorting import group_class_acceptabilities_validation

__all__ = ["calculate_alternatives_support"]


def _calculate_votes(
    alternatives: pd.Index,
    categories: List[str],
    assignments: List[pd.DataFrame],
) -> pd.DataFrame:
    """
    This function calculates how many votes are for putting each alternative
    in each category.

    :param alternatives: pd.Index with alternatives names
    :param categories: List of categories names as strings
    :param assignments: List of pd.DataFrames with alternatives as index and
        'worse' and 'better' columns. Each DataFrame represents
        imprecise assignment of one DM.
    :return: pd.DataFrame with alternatives as index
        and categories as columns. Contains number of votes for each
        alternative in each category
    """

    # Create votes DataFrame with zeros
    votes = pd.DataFrame(
        [[0 for __ in categories] for _ in alternatives],
        index=alternatives,
        columns=categories,
    )

    # Count votes
    for DM_i, DM_assignments in enumerate(assignments):
        for alternative, alternative_row in DM_assignments.iterrows():
            # Handles precise assignments
            if alternative_row["worse"] == alternative_row["better"]:
                votes.loc[alternative, alternative_row["worse"]] += 1
            # Handles imprecise assignments
            else:
                votes.loc[
                    alternative,
                    alternative_row["worse"] : alternative_row["better"],
                ] += 1

    return votes


def _calculate_alternatives_support(
    assignments: List[pd.DataFrame], votes: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculates basic alternatives support for each alternative and category
     (percentage).

    :param assignments: List of pd.DataFrames with alternatives as index and
        'worse' and 'better' columns. Each DataFrame represents
    :param votes: pd.DataFrame with alternatives as index
        and categories as columns. Contains number of votes for each
        alternative in each category
    :return: pd.DataFrame with alternatives as index and categories
        as columns. Contains for each alternative the percentage of
        votes assigned for each category
    """

    # Get number of DMs
    n_DM = len(assignments)

    # Divide votes by number of DMs and multiply by 100 to get percentage
    alternatives_support = votes / n_DM * 100

    return alternatives_support


def _calculate_unimodal_alternatives_support(
    alternatives_support: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculates uni-modal alternatives support for each alternative
     and category (percentage).

    :param alternatives_support: pd.DataFrame with alternatives as index
        and categories as columns. Contains for each alternative the percentage
         of votes assigned for each category

    :return: pd.DataFrame with alternatives as index
        and categories as columns. Contains for each alternative the uni-modal
        percentage of votes assigned for each category

    """

    # Calculate unimodal alternatives support for single row of DataFrame
    def unimodal_single_row(row: pd.Series) -> pd.Series:
        """
        Simple function with logic for calculating uni-modal support for
        alternative.

        :param row: pd.Series with categories as index and basic support
            for alternative as values
        :return: pd.Series with categories as index and uni-modal support
            for alternative as values
        """

        # Get number of categories
        row_len = len(row)

        # Init uni-modal support row
        unimodal_row = pd.Series([0 for _ in range(row_len)], index=row.index)

        # Iterate over basic alternative support to detect specific cases
        # and fix them
        for i, (category, support) in enumerate(row.items()):
            # Edge case - first or last category
            if i == 0 or i == row_len - 1:
                unimodal_row[category] = support
            else:
                unimodal_row[category] = max(
                    support, min(max(row.iloc[:i]), max(row.iloc[i + 1 :]))
                )
        return unimodal_row

    unimodal_alternatives_support = cast(
        pd.DataFrame,
        alternatives_support.apply(unimodal_single_row, axis=1).astype(float),
    )

    return unimodal_alternatives_support


def calculate_alternatives_support(
    categories: List[str], assignments: List[pd.DataFrame]
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Transforms DM assignments, count votes and basing on them calculates
     alternatives support and uni-modal alternatives support

    :param categories: List of categories names as strings
    :param assignments: List of pd.DataFrames with alternatives as index and
        'worse' and 'better' columns. Each DataFrame represents
        imprecise assignment of one DM.

    :return: Tuple with pd.DataFrame with alternatives as index and categories
        as columns and pd.DataFrame with alternatives as index and categories
        as columns. First DataFrame represents basic alternatives support
        and second uni-modal alternatives support, which has aligned support
        for categories where its left and right neighbour have higher basic
        support
    """

    # Input validaiotn
    group_class_acceptabilities_validation(categories, assignments)

    # Get alternatives names
    alternatives = assignments[0].index

    # Calculate votes
    votes = _calculate_votes(alternatives, categories, assignments)
    # Calculate basic alternatives support
    alternatives_support = _calculate_alternatives_support(assignments, votes)
    # Calculate uni-modal alternatives support
    unimodal_alternatives_support = _calculate_unimodal_alternatives_support(
        alternatives_support
    )

    return alternatives_support, unimodal_alternatives_support
