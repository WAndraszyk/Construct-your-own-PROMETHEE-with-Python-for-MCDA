"""
    This module calculates alternatives support (basic and unimodal).
"""
import math
import pandas as pd
from typing import List, Tuple
from core.input_validation import group_class_acceptabilities_validation

__all__ = ["calculate_alternatives_support"]


def _calculate_votes(alternatives: List[str], categories: List[str],
                     assignments: List[pd.DataFrame]) -> pd.DataFrame:
    """
    This function calculates how many votes are for putting each alternative
    in each category.

    :param alternatives: List with alternatives names as strings
    :param categories: List with categories names as strings
    :param assignments: List with pd.DataFrame objects with alternatives as
    index and assignments as columns named (worse and better)

    :return: pd.DataFrame with alternatives names as index and categories
    names as columns
    """
    votes = pd.DataFrame([[0 for __ in categories] for _ in alternatives],
                         index=alternatives,
                         columns=categories)
    for DM_i, DM_assignments in enumerate(assignments):
        for alternative, alternative_row in DM_assignments.iterrows():
            if alternative_row['worse'] == alternative_row['better']:
                votes.loc[alternative, alternative_row['worse']] += 1
            else:
                votes.loc[alternative,
                alternative_row['worse']:alternative_row['better']] += 1

    return votes


def _calculate_alternatives_support(assignments: List[pd.DataFrame],
                                    votes: pd.DataFrame) -> pd.DataFrame:
    """
    This function calculates alternatives support for each alternative
    and category (percentage).

    :param assignments: List with pd.DataFrame objects with alternatives as
    index and assignments as columns named (worse and better)
    :param votes: pd.DataFrame with alternatives names as index and categories
    names as columns

    :return: pd.DataFrame with alternatives names as index and categories
    names as columns
    """
    n_DM = len(assignments)
    alternatives_support = votes / n_DM * 100

    return alternatives_support


def _calculate_unimodal_alternatives_support(
        alternatives_support: pd.DataFrame) -> pd.DataFrame:
    """
    This function calculates unimodal alternatives support for each
    alternative and category (percentage).

    :param alternatives_support: pd.DataFrame with alternatives names as index
    and categories names as columns

    :return: pd.DataFrame with alternatives names as index and categories
    names as columns
    """

    # Calculate unimodal alternatives support for single row of DataFrame
    def unimodal_single_row(row: pd.Series) -> pd.Series:
        row_len = len(row)
        unimodal_row = pd.Series([0 for _ in range(row_len)], index=row.index)

        for i, (category, support) in enumerate(row.items()):
            if math.isclose(i, 0) or math.isclose(i, (row_len - 1)):
                unimodal_row[category] = support
            else:
                unimodal_row[category] = max(support,
                                             min(max(row.iloc[:i]),
                                                 max(row.iloc[i + 1:])))
        return unimodal_row

    unimodal_alternatives_support = alternatives_support.apply(
        unimodal_single_row, axis=1).astype(float)

    return unimodal_alternatives_support


def calculate_alternatives_support(categories: List[str],
                                   assignments: List[pd.DataFrame]
                                   ) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    This function transforms DM assignments, count votes and basing on them
    calculates alternatives support and unimodal alternatives support.

    :param categories: List with categories names as strings
    :param assignments: List with pd.DataFrame objects with alternatives as
    index and assignments as columns named (worse and better)

    :return: Tuple with pd.DataFrame objects with alternatives names as index
    and categories names as columns
    """
    group_class_acceptabilities_validation(categories, assignments)
    alternatives = list(assignments[0].index)

    votes = _calculate_votes(alternatives, categories, assignments)
    alternatives_support = _calculate_alternatives_support(assignments, votes)
    unimodal_alternatives_support = _calculate_unimodal_alternatives_support(
        alternatives_support)

    return alternatives_support, unimodal_alternatives_support
