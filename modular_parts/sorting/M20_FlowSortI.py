"""
    This module computes the assignments of given alternatives to categories
    using FlowSort procedure based on PrometheeI flows.

    Implementation and naming of conventions are taken from
    :cite:p:'NemeryLamboray2007'.
"""

import pandas as pd
from typing import List, Hashable
from core.enums import CompareProfiles
from core.preference_commons import directed_alternatives_performances
from core.promethee_check_dominance import check_dominance_condition
from core.input_validation import flow_sort_i_validation

__all__ = ["calculate_flowsortI_sorted_alternatives"]


def _append_to_classification(
        categories: List[str], classification: pd.DataFrame,
        pessimistic_category: str,
        optimistic_category: str, alternative_name: Hashable) -> None:
    """
    This function assign alternatives to correctly class.

    :param categories: List with categories names as strings
    :param classification: pd.DataFrame with alternatives as index and
    assignments as columns named (worse and better)
    :param pessimistic_category: str that determines category names chosen of
    negative flow
    :param optimistic_category: str that determines category name chosen of
    positive flow
    :param alternative_name: Hashable that determines the alternative name
    assigned to the category
    """
    pessimistic_category_index = categories.index(pessimistic_category)
    optimistic_category_index = categories.index(optimistic_category)
    if pessimistic_category_index > optimistic_category_index:
        pessimistic_category, optimistic_category = optimistic_category, \
                                                    pessimistic_category

    classification.loc[alternative_name, 'worse'] = pessimistic_category
    classification.loc[alternative_name, 'better'] = optimistic_category


def _limiting_profiles_sorting(categories: List[str],
                               alternatives_flows: pd.DataFrame,
                               category_profiles_flows: pd.DataFrame
                               ) -> pd.DataFrame:
    """
    This function compares positive and negative flows of each alternative
    with all limiting profiles and assign them to correctly class.

    :param categories: List with categories names as strings
    :param alternatives_flows: pd.DataFrame with alternatives as
    index and flows as columns named (positive and negative)
    :param category_profiles_flows: pd.DataFrame with alternatives as
    index and flows as columns named (positive and negative)

    :return: pd.DataFrame with alternatives as index and assignments as
    columns named (worse and better)
    """

    classification = pd.DataFrame(index=alternatives_flows.index,
                                  columns=['worse', 'better'], dtype=str)

    for alternative, alternative_row in alternatives_flows.iterrows():
        positive_flow_category = ''
        negative_flow_category = ''
        for i, (category, category_row) in enumerate(
                category_profiles_flows.iterrows()):
            if not positive_flow_category:
                if i != len(category_profiles_flows) - 1:
                    if category_row['positive'] < alternative_row[
                        'positive'] <= category_profiles_flows.iloc[i + 1][
                         'positive']:
                        positive_flow_category = categories[i]
            if not negative_flow_category:
                if i != len(category_profiles_flows) - 1:
                    if category_row['negative'] >= \
                            alternative_row['negative'] \
                            > category_profiles_flows.iloc[i + 1]['negative']:
                        negative_flow_category = categories[i]
            if positive_flow_category and negative_flow_category:
                _append_to_classification(categories, classification,
                                          negative_flow_category,
                                          positive_flow_category, alternative)
                break

    return classification


def _boundary_profiles_sorting(categories: List[str],
                               category_profiles: pd.DataFrame,
                               alternatives_flows: pd.DataFrame,
                               category_profiles_flows: pd.DataFrame
                               ) -> pd.DataFrame:
    """
    This function compares positive and negative flows of each alternative
    with all boundary profiles and assign them to correctly class.

    :param categories: List with categories names as strings
    :param category_profiles: pd.DataFrame with profiles as index and criteria
    as columns
    :param alternatives_flows: pd.DataFrame with alternatives as
    index and flows as columns named (positive and negative)
    :param category_profiles_flows: pd.DataFrame with alternatives as
    index and flows as columns named (positive and negative)

    :return: pd.DataFrame with alternatives as index and assignments as
    columns named (worse and better)
    """
    classification = pd.DataFrame(index=alternatives_flows.index,
                                  columns=['worse', 'better'], dtype=str)

    for alternative, alternative_row in alternatives_flows.iterrows():
        positive_flow_category = ''
        negative_flow_category = ''
        for i, (category, category_row) in enumerate(
                category_profiles_flows.iterrows()):
            if not positive_flow_category:
                if i == 0:
                    if alternative_row['positive'] <= category_row[
                         'positive']:
                        positive_flow_category = categories[i]
                elif i == category_profiles.shape[0] - 1:
                    if alternative_row['positive'] > \
                            category_profiles_flows.iloc[i - 1]['positive']:
                        positive_flow_category = categories[i]
                else:
                    if category_profiles_flows.iloc[i - 1]['positive'] < \
                            alternative_row['positive'] <= category_row[
                         'positive']:
                        positive_flow_category = categories[i]
            if not negative_flow_category:
                if i == 0:
                    if alternative_row['negative'] > category_row['negative']:
                        negative_flow_category = categories[i]
                elif i == len(category_profiles) - 1:
                    if alternative_row['negative'] <= \
                            category_profiles_flows.iloc[i - 1]['negative']:
                        negative_flow_category = categories[i]
                else:
                    if category_profiles_flows.iloc[i - 1]['negative'] >= \
                            alternative_row['negative'] > category_row[
                         'negative']:
                        negative_flow_category = categories[i]
            if positive_flow_category and negative_flow_category:
                _append_to_classification(categories, classification,
                                          negative_flow_category,
                                          positive_flow_category,
                                          alternative)
                break

    return classification


def _central_profiles_sorting(categories: List[str],
                              category_profiles: pd.DataFrame,
                              alternatives_flows: pd.DataFrame,
                              category_profiles_flows: pd.DataFrame
                              ) -> pd.DataFrame:
    """
    This function compares positive and negative flows of each alternative
    with all central profiles and assign them to correct class.

    :param categories: List with categories names as strings
    :param category_profiles: pd.DataFrame with profiles as index and criteria
    as columns
    :param alternatives_flows: pd.DataFrame with alternatives as
    index and flows as columns named (positive and negative)
    :param category_profiles_flows: pd.DataFrame with alternatives as
    index and flows as columns named (positive and negative)

    :return: pd.DataFrame with alternatives as index and assignments as
    columns named (worse and better)
    """
    classification = pd.DataFrame(index=alternatives_flows.index,
                                  columns=['worse', 'better'], dtype=str)

    for alternative, alternative_row in alternatives_flows.iterrows():
        positive_flow_category = ''
        negative_flow_category = ''
        for i, (category, category_row) in enumerate(
                category_profiles_flows.iterrows()):
            if not positive_flow_category:
                if i == 0:
                    if alternative_row['positive'] <= \
                            (category_row['positive'] +
                             category_profiles_flows.iloc[i + 1][
                                 'positive']) / 2:
                        positive_flow_category = categories[i]
                elif i == len(category_profiles) - 1:
                    if (category_profiles_flows.iloc[i - 1]['positive'] +
                        category_row['positive']) / 2 < \
                            alternative_row['positive']:
                        positive_flow_category = categories[i]
                else:
                    if (category_profiles_flows.iloc[i - 1]['positive'] +
                        category_row['positive']) / 2 < \
                            alternative_row['positive'] <= \
                            (category_row['positive'] +
                             category_profiles_flows.iloc[i + 1][
                                 'positive']) / 2:
                        positive_flow_category = categories[i]
            if not negative_flow_category:
                if i == 0:
                    if alternative_row['negative'] > \
                            (category_row['negative'] +
                             category_profiles_flows.iloc[i + 1][
                                 'negative']) / 2:
                        negative_flow_category = categories[i]
                elif i == len(category_profiles) - 1:
                    if (category_profiles_flows.iloc[i - 1]['negative'] +
                        category_row['negative']) / 2 >= \
                            alternative_row['negative']:
                        negative_flow_category = categories[i]
                else:
                    if (category_profiles_flows.iloc[i - 1]['negative'] +
                        category_row['negative']) / 2 >= \
                            alternative_row['negative'] > \
                            (category_row['negative'] +
                             category_profiles_flows.iloc[i + 1][
                                 'negative']) / 2:
                        negative_flow_category = categories[i]
            if positive_flow_category and negative_flow_category:
                _append_to_classification(categories, classification,
                                          negative_flow_category,
                                          positive_flow_category,
                                          alternative)
                break
    return classification


def calculate_flowsortI_sorted_alternatives(
        categories: List[str],
        category_profiles: pd.DataFrame,
        criteria_directions: pd.Series,
        alternatives_flows: pd.DataFrame,
        category_profiles_flows: pd.DataFrame,
        comparison_with_profiles: CompareProfiles) -> pd.DataFrame:
    """
    This function sorts alternatives to proper categories
    (based on FlowSort I).

    :param categories: List with categories names as strings
    :param category_profiles: pd.DataFrame with profiles as index and criteria
    as columns
    :param criteria_directions: pd.Series with criteria as index and
    Direction as values
    :param alternatives_flows: pd.DataFrame with alternatives as
    index and flows as columns named (positive and negative)
    :param category_profiles_flows: pd.DataFrame with alternatives as
    index and flows as columns named (positive and negative)
    :param comparison_with_profiles: CompareProfiles - indicate
    information of profiles types used in calculation.

    :return: pd.DataFrame with alternatives as index and assignments as
    columns named (worse and better)
    """
    flow_sort_i_validation(categories, category_profiles, criteria_directions,
                           alternatives_flows, category_profiles_flows,
                           comparison_with_profiles)

    check_dominance_condition(criteria_directions, category_profiles)

    category_profiles = directed_alternatives_performances(
        category_profiles, criteria_directions)

    if comparison_with_profiles == CompareProfiles.LIMITING_PROFILES:
        return _limiting_profiles_sorting(categories, alternatives_flows,
                                          category_profiles_flows)
    elif comparison_with_profiles == CompareProfiles.BOUNDARY_PROFILES:
        return _boundary_profiles_sorting(categories, category_profiles,
                                          alternatives_flows,
                                          category_profiles_flows)
    else:
        return _central_profiles_sorting(categories, category_profiles,
                                         alternatives_flows,
                                         category_profiles_flows)
