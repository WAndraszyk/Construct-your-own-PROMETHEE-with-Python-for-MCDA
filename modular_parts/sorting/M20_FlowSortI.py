"""
    This module computes the assignments of given alternatives to categories using FlowSort procedure based on
    PrometheeI flows.
"""

import pandas as pd
from typing import List, Hashable
from core.enums import CompareProfiles
from core.preference_commons import directed_alternatives_performances
from core.promethee_check_dominance import check_dominance_condition
from core.input_validation import flow_sort_i_validation

__all__ = ["calculate_flowsortI_sorted_alternatives"]


def _append_to_classification(categories: List[str], classification: pd.DataFrame, pessimistic_category: str,
                              optimistic_category: str, alternative_name: Hashable) -> None:
    pessimistic_category_index = categories.index(pessimistic_category)
    optimistic_category_index = categories.index(optimistic_category)
    if pessimistic_category_index > optimistic_category_index:
        pessimistic_category, optimistic_category = optimistic_category, pessimistic_category

    classification.loc[alternative_name, 'worse'] = pessimistic_category
    classification.loc[alternative_name, 'better'] = optimistic_category


def _limiting_profiles_sorting(categories: List[str], alternatives_flows: pd.DataFrame,
                               category_profiles_flows: pd.DataFrame) -> pd.DataFrame:
    """
    Comparing positive and negative flows of each alternative with all limiting profiles and assign them to
    correctly class.

    :param categories: List of categories names (strings only)
    :param alternatives_flows: Flows table with alternatives flows
    :param category_profiles_flows: Flows table with category profiles flows

    :return: DataFrame with alternatives assigned to proper classes
    """

    classification = pd.DataFrame(index=alternatives_flows.index, columns=['worse', 'better'], dtype=str)

    for alternative, alternative_row in alternatives_flows.iterrows():
        positive_flow_category = ''
        negative_flow_category = ''
        for i, (category, category_row) in enumerate(category_profiles_flows.iterrows()):
            if not positive_flow_category:
                if i != len(category_profiles_flows) - 1:
                    if category_row['positive'] < alternative_row['positive'] \
                            <= category_profiles_flows.iloc[i + 1]['positive']:
                        positive_flow_category = categories[i]
            if not negative_flow_category:
                if i != len(category_profiles_flows) - 1:
                    if category_row['negative'] >= alternative_row['negative'] \
                            > category_profiles_flows.iloc[i + 1]['negative']:
                        negative_flow_category = categories[i]
            if positive_flow_category and negative_flow_category:
                _append_to_classification(categories, classification, negative_flow_category,
                                          positive_flow_category, alternative)
                break

    return classification


def _boundary_profiles_sorting(categories: List[str], category_profiles: pd.DataFrame,
                               alternatives_flows: pd.DataFrame, category_profiles_flows: pd.DataFrame) -> pd.DataFrame:
    """
    Comparing positive and negative flows of each alternative with all boundary profiles and assign them to
    correctly class.

    :param categories: List of categories names (strings only)
    :param category_profiles: Preference table with category profiles
    :param alternatives_flows: Flows table with alternatives flows
    :param category_profiles_flows: Flows table with category profiles flows

    :return: DataFrame with alternatives assigned to proper classes
    """
    classification = pd.DataFrame(index=alternatives_flows.index, columns=['worse', 'better'], dtype=str)

    for alternative, alternative_row in alternatives_flows.iterrows():
        positive_flow_category = ''
        negative_flow_category = ''
        for i, (category, category_row) in enumerate(category_profiles_flows.iterrows()):
            if not positive_flow_category:
                if i == 0:
                    if alternative_row['positive'] <= category_row['positive']:
                        positive_flow_category = categories[i]
                elif i == category_profiles.shape[0] - 1:
                    if alternative_row['positive'] > category_profiles_flows.iloc[i - 1]['positive']:
                        positive_flow_category = categories[i]
                else:
                    if category_profiles_flows.iloc[i - 1]['positive'] < \
                            alternative_row['positive'] <= category_row['positive']:
                        positive_flow_category = categories[i]
            if not negative_flow_category:
                if i == 0:
                    if alternative_row['negative'] > category_row['negative']:
                        negative_flow_category = categories[i]
                elif i == len(category_profiles) - 1:
                    if alternative_row['negative'] <= category_profiles_flows.iloc[i - 1]['negative']:
                        negative_flow_category = categories[i]
                else:
                    if category_profiles_flows.iloc[i - 1]['negative'] >= \
                            alternative_row['negative'] > category_row['negative']:
                        negative_flow_category = categories[i]
            if positive_flow_category and negative_flow_category:
                _append_to_classification(categories, classification, negative_flow_category, positive_flow_category,
                                          alternative)
                break

    return classification


def _central_profiles_sorting(categories: List[str], category_profiles: pd.DataFrame,
                              alternatives_flows: pd.DataFrame, category_profiles_flows: pd.DataFrame) -> pd.DataFrame:
    """
    Comparing positive and negative flows of each alternative with all central profiles and assign them to
    correctly class.

    :param categories: List of categories names (strings only)
    :param category_profiles: Preference table with category profiles
    :param alternatives_flows: Flows table with alternatives flows
    :param category_profiles_flows: Flows table with category profiles flows

    :return: DataFrame with alternatives assigned to proper classes
    """
    classification = pd.DataFrame(index=alternatives_flows.index, columns=['worse', 'better'], dtype=str)

    for alternative, alternative_row in alternatives_flows.iterrows():
        positive_flow_category = ''
        negative_flow_category = ''
        for i, (category, category_row) in enumerate(category_profiles_flows.iterrows()):
            if not positive_flow_category:
                if i == 0:
                    if alternative_row['positive'] <= \
                            (category_row['positive'] + category_profiles_flows.iloc[i + 1]['positive']) / 2:
                        positive_flow_category = categories[i]
                elif i == len(category_profiles) - 1:
                    if (category_profiles_flows.iloc[i - 1]['positive'] + category_row['positive']) / 2 < \
                            alternative_row['positive']:
                        positive_flow_category = categories[i]
                else:
                    if (category_profiles_flows.iloc[i - 1]['positive'] + category_row['positive']) / 2 < \
                            alternative_row['positive'] <= \
                            (category_row['positive'] + category_profiles_flows.iloc[i + 1]['positive']) / 2:
                        positive_flow_category = categories[i]
            if not negative_flow_category:
                if i == 0:
                    if alternative_row['negative'] > \
                            (category_row['negative'] + category_profiles_flows.iloc[i + 1]['negative']) / 2:
                        negative_flow_category = categories[i]
                elif i == len(category_profiles) - 1:
                    if (category_profiles_flows.iloc[i - 1]['negative'] + category_row['negative']) / 2 >= \
                            alternative_row['negative']:
                        negative_flow_category = categories[i]
                else:
                    if (category_profiles_flows.iloc[i - 1]['negative'] + category_row['negative']) / 2 >= \
                            alternative_row['negative'] > \
                            (category_row['negative'] + category_profiles_flows.iloc[i + 1]['negative']) / 2:
                        negative_flow_category = categories[i]
            if positive_flow_category and negative_flow_category:
                _append_to_classification(categories, classification, negative_flow_category, positive_flow_category,
                                          alternative)
                break
    return classification


def calculate_flowsortI_sorted_alternatives(categories: List[str],
                                            category_profiles: pd.DataFrame,
                                            criteria_directions: pd.Series,
                                            alternatives_flows: pd.DataFrame,
                                            category_profiles_flows: pd.DataFrame,
                                            comparison_with_profiles: CompareProfiles) -> pd.DataFrame:
    """
    Sort alternatives to proper categories.

    :param categories: List of categories names (strings only)
    :param category_profiles: Performances table with category profiles
    :param criteria_directions: Series with criteria directions
    :param alternatives_flows: Flows table with alternatives flows
    :param category_profiles_flows: Flows table with category profiles flows
    :param comparison_with_profiles: Enum CompareProfiles - indicate information of profiles types used in calculation.

    :return: DataFrame with alternatives assigned to proper classes
    """
    flow_sort_i_validation(categories, category_profiles, criteria_directions,
                           alternatives_flows, category_profiles_flows, comparison_with_profiles)

    check_dominance_condition(criteria_directions, category_profiles)

    category_profiles = directed_alternatives_performances(category_profiles, criteria_directions)

    if comparison_with_profiles == CompareProfiles.LIMITING_PROFILES:
        return _limiting_profiles_sorting(categories, alternatives_flows, category_profiles_flows)
    elif comparison_with_profiles == CompareProfiles.BOUNDARY_PROFILES:
        return _boundary_profiles_sorting(categories, category_profiles, alternatives_flows, category_profiles_flows)
    else:
        return _central_profiles_sorting(categories, category_profiles, alternatives_flows, category_profiles_flows)
