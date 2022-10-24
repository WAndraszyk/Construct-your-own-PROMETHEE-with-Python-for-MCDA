"""
    This module computes the assignments of given alternatives to categories using FlowSort procedure based on
    Promethee II flows.
"""

import pandas as pd
from typing import List
from core.enums import CompareProfiles
from core.aliases import PerformanceTable
from core.sorting import pandas_check_dominance_condition

__all__ = ["calculate_flowsort2_sorted_alternatives"]


def _limiting_profiles_sorting(categories: List[str], category_profiles: PerformanceTable,
                               alternatives_flows: pd.Series, category_profiles_flows: pd.Series) -> pd.Series:
    """
    Comparing positive and negative flows of each alternative with all limiting profiles and assign them to
    correctly class.

    :param categories: List of categories names (strings only)
    :param category_profiles: DataFrame with category profiles performances
    :param alternatives_flows: Series with alternatives names as index and net flows as values
    :param category_profiles_flows: Series with categories names as index and net flows as values

    :return: Series with alternatives classification
    """
    classification = pd.Series(['None' for _ in alternatives_flows.index], index=alternatives_flows.index)

    for alternative, alternative_net_flow in alternatives_flows.items():
        for i, category, category_net_flow in enumerate(list(category_profiles_flows.items())[:-1]):
            if category_net_flow < alternative_net_flow <= category_profiles[i + 1]:
                classification[alternative] = categories[i]
    return classification


def _boundary_profiles_sorting(categories: List[str], category_profiles: PerformanceTable,
                               alternatives_flows: pd.Series, category_profiles_flows: pd.Series) -> pd.Series:
    """
    Comparing positive and negative flows of each alternative with all boundary profiles and assign them to
    correctly class.

    :param categories: List of categories names (strings only)
    :param category_profiles: DataFrame with category profiles performances
    :param alternatives_flows: Series with alternatives names as index and net flows as values
    :param category_profiles_flows: Series with categories names as index and net flows as values

    :return: Series with alternatives classification
    """
    classification = pd.Series(['None' for _ in alternatives_flows.index], index=alternatives_flows.index)

    for alternative, alternative_net_flow in alternatives_flows.items():
        for i, category, category_net_flow in enumerate(category_profiles_flows.items()):
            if i == 0:
                if alternative_net_flow <= category_net_flow:
                    classification[alternative] = categories[i]
                    break
            elif i == category_profiles.shape[0] - 1:
                if category_profiles_flows[i - 1] < alternative_net_flow:
                    classification[alternative] = categories[i]
            else:
                if category_profiles_flows[i - 1] < alternative_net_flow <= category_net_flow:
                    classification[alternative] = categories[i]
                    break
    return classification


def _central_profiles_sorting(categories: List[str], category_profiles: PerformanceTable,
                              alternatives_flows: pd.Series, category_profiles_flows: pd.Series) -> pd.Series:
    """
    Comparing positive and negative flows of each alternative with all central profiles and assign them to
    correctly class.

    :param categories: List of categories names (strings only)
    :param category_profiles: DataFrame with category profiles performances
    :param alternatives_flows: Series with alternatives names as index and net flows as values
    :param category_profiles_flows: Series with categories names as index and net flows as values

    :return: Series with alternatives classification
    """
    classification = pd.Series(['None' for _ in alternatives_flows.index], index=alternatives_flows.index)

    for alternative, alternative_net_flow in alternatives_flows.items():
        for i, category, category_net_flow in enumerate(category_profiles_flows.items()):
            if i == 0:
                if alternative_net_flow <= (category_net_flow + category_profiles_flows[i + 1]) / 2:
                    classification[alternative] = categories[i]
                    break
            elif i == category_profiles.shape[0] - 1:
                if (category_profiles_flows[i - 1] + category_net_flow) / 2 < alternative_net_flow:
                    classification[alternative] = categories[i]
            else:
                if (category_profiles_flows[i - 1] + category_net_flow) / 2 < alternative_net_flow \
                        <= (category_net_flow + category_profiles_flows[i + 1]) / 2:
                    classification[alternative] = categories[i]
                    break
    return classification


def calculate_flowsort2_sorted_alternatives(categories: List[str],
                                            category_profiles: PerformanceTable,
                                            criteria_directions: pd.Series,
                                            alternatives_flows: pd.Series,
                                            category_profiles_flows: pd.Series,
                                            comparison_with_profiles: CompareProfiles) -> pd.Series:
    """
    Sort alternatives to proper categories.

    :param categories: List of categories names (strings only)
    :param category_profiles: DataFrame with category profiles performances
    :param criteria_directions: Series with criteria directions (max or min)
    :param alternatives_flows: Series with alternatives names as index and net flows as values
    :param category_profiles_flows: Series with categories names as index and net flows as values
    :param comparison_with_profiles: Enum CompareProfiles - indicate information of profiles types used
    in calculation.

    :return: Dictionary with alternatives assigned to proper classes
    """
    pandas_check_dominance_condition(criteria_directions, category_profiles)

    if comparison_with_profiles == CompareProfiles.LIMITING_PROFILES:
        return _limiting_profiles_sorting(categories, category_profiles, alternatives_flows, category_profiles_flows)
    elif comparison_with_profiles == CompareProfiles.BOUNDARY_PROFILES:
        return _boundary_profiles_sorting(categories, category_profiles, alternatives_flows, category_profiles_flows)
    else:
        return _central_profiles_sorting(categories, category_profiles, alternatives_flows, category_profiles_flows)
