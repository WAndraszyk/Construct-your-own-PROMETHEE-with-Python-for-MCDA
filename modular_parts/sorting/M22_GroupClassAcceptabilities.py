"""
    This module calculates alternatives support (basic and unimodal).
"""
import math

import pandas as pd
from typing import List, Tuple
from core.input_validation.sorting_input_validation import alternatives_support_validation

__all__ = ["calculate_alternatives_support"]


def _calculate_votes(alternatives: List[str], categories: List[str], assignments: List[pd.DataFrame]) -> pd.DataFrame:
    """
    Calculate how many votes are for putting each alternative in each category.

    :param alternatives: List of alternatives names (strings only)
    :param categories: List of categories names (strings only)
    :param assignments: List of imprecise alternatives assignments of each DM

    :return: DataFrame with votes for each category for each alternative (index: alternatives, columns: categories)
    """
    votes = pd.DataFrame([[0 for __ in categories] for _ in alternatives], index=alternatives,
                         columns=categories)
    for DM_i, DM_assignments in enumerate(assignments):
        for alternative, alternative_row in DM_assignments.iterrows():
            if alternative_row['worse'] == alternative_row['better']:
                votes.loc[alternative, alternative_row['worse']] += 1
            else:
                votes.loc[alternative, alternative_row['worse']:alternative_row['better']] += 1

    return votes


def _calculate_alternatives_support(assignments: List[pd.DataFrame], votes: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates alternatives support for each alternative and category (percentage).

    :param assignments: List of imprecise alternatives assignments of each DM
    :param votes: DataFrame with votes for each category
     for each alternative (index: alternatives, columns: categories)

    :return: DataFrame with alternative support for each category
     for each alternative (index: alternatives, columns: categories)
    """
    n_DM = len(assignments)
    alternatives_support = votes / n_DM * 100

    return alternatives_support


def _calculate_unimodal_alternatives_support(alternatives_support: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates unimodal alternatives support for each alternative and category (percentage).

    :param alternatives_support: 2D List with alternative support for each category for each alternative

    :return: 2D List with unimodal alternative support for each category for each alternative
    """

    def unimodal_single_row(row: pd.Series) -> pd.Series:
        row_len = len(row)
        unimodal_row = pd.Series([0 for _ in range(row_len)], index=row.index)

        for i, (category, support) in enumerate(row.items()):
            if math.isclose(i, 0) or math.isclose(i, (row_len - 1)):
                unimodal_row[category] = support
            else:
                unimodal_row[category] = max(support, min(max(row.iloc[:i]), max(row.iloc[i + 1:])))
        return unimodal_row

    unimodal_alternatives_support = alternatives_support.apply(unimodal_single_row, axis=1).astype(float)

    return unimodal_alternatives_support


def calculate_alternatives_support(categories: List[str],
                                   assignments: List[pd.DataFrame]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Transforms DM assignments, count votes and basing on them calculates alternatives support and
     unimodal alternatives support

    :param categories: List of categories names (strings only)
    :param assignments: List of imprecise alternatives assignments of each DM

    :return: Tuple with DataFrames as alternatives support and unimodal alternatives support
    """
    alternatives_support_validation(categories, assignments)
    alternatives = list(assignments[0].index)

    votes = _calculate_votes(alternatives, categories, assignments)
    alternatives_support = _calculate_alternatives_support(assignments, votes)
    unimodal_alternatives_support = _calculate_unimodal_alternatives_support(alternatives_support)

    return alternatives_support, unimodal_alternatives_support
