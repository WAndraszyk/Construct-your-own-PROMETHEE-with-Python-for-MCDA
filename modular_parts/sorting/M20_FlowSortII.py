"""
    This module computes the assignments of given alternatives to categories using FlowSort procedure based on
    Promethee II flows.
"""
import math

import pandas as pd
from typing import List
from core.enums import CompareProfiles
from core.aliases import PerformanceTable
from core.promethee_check_dominance import check_dominance_condition

__all__ = ["calculate_flowsortII_sorted_alternatives"]


def _limiting_profiles_sorting(categories: List[str], prometheeII_net_flows: pd.Series) -> pd.Series:
    """
    Comparing positive and negative flows of each alternative with all limiting profiles and assign them to
    correctly class.

    :param categories: List of categories names (strings only)
    :param prometheeII_net_flows: Series with Promethee II net flows

    :return: Series with alternatives classification
    """
    classification = pd.Series(dtype=str)

    for Ralternative, alternative_group_net_flow in prometheeII_net_flows.groupby(level=0):
        alternative = Ralternative[1:]
        profiles_net_flows = alternative_group_net_flow.iloc[:-1]
        alternative_net_flow = alternative_group_net_flow.iloc[-1]

        for i, (profile, profile_net_flow) in enumerate(profiles_net_flows.items()):
            if alternative_net_flow <= profile_net_flow:
                if i == 0:
                    classification[alternative] = "Under limit"
                else:
                    classification[alternative] = categories[i - 1]
                break
            elif i == (len(profiles_net_flows) - 1):
                classification[alternative] = "Over limit"

    return classification


def _boundary_profiles_sorting(categories: List[str], category_profiles: PerformanceTable,
                               prometheeII_net_flows: pd.Series) -> pd.Series:
    """
    Comparing positive and negative flows of each alternative with all boundary profiles and assign them to
    correctly class.

    :param categories: List of categories names (strings only)
    :param category_profiles: DataFrame with category profiles performances
    :param prometheeII_net_flows: Series with Promethee II net flows

    :return: Series with alternatives classification
    """
    classification = pd.Series(dtype=str)

    for Ralternative, alternative_group_net_flow in prometheeII_net_flows.groupby(level=0):
        alternative = Ralternative[1:]
        profiles_net_flows = alternative_group_net_flow.iloc[:-1]
        alternative_net_flow = alternative_group_net_flow.iloc[-1]

        for i, (profile, profile_net_flow) in enumerate(profiles_net_flows.items()):
            if alternative_net_flow <= profile_net_flow:
                classification[alternative] = categories[i]
                break
            elif i == (len(profiles_net_flows) - 1):
                classification[alternative] = categories[-1]

    return classification


def _central_profiles_sorting(categories: List[str], category_profiles: PerformanceTable,
                              prometheeII_net_flows) -> pd.Series:
    """
    Comparing positive and negative flows of each alternative with all central profiles and assign them to
    correctly class.

    :param categories: List of categories names (strings only)
    :param category_profiles: DataFrame with category profiles performances
    :param prometheeII_net_flows: Series with Promethee II net flows

    :return: Series with alternatives classification
    """
    classification = pd.Series(dtype=str)

    for Ralternative, alternative_group_net_flow in prometheeII_net_flows.groupby(level=0):
        alternative = Ralternative[1:]
        profiles_net_flows = alternative_group_net_flow.iloc[:-1]
        alternative_net_flow = alternative_group_net_flow.iloc[-1]

        for i, (profile, profile_net_flow) in enumerate(profiles_net_flows.items()):
            if i == (len(profiles_net_flows) - 1):
                if alternative_net_flow > (profile_net_flow + profiles_net_flows.iloc[i - 1]) / 2:
                    classification[alternative] = categories[i]
                    break
            else:
                if alternative_net_flow <= (profile_net_flow + profiles_net_flows.iloc[i + 1]) / 2:
                    classification[alternative] = categories[i]
                    break

    return classification


def calculate_flowsortII_sorted_alternatives(categories: List[str],
                                             category_profiles: PerformanceTable,
                                             criteria_directions: pd.Series,
                                             prometheeII_net_flows: pd.Series,
                                             comparison_with_profiles: CompareProfiles) -> pd.Series:
    """
    Sort alternatives to proper categories.

    :param categories: List of categories names (strings only)
    :param category_profiles: DataFrame with category profiles performances
    :param criteria_directions: Series with criteria directions (max or min)
    :param prometheeII_net_flows: DataFrame with Promethee II flows
    :param comparison_with_profiles: Enum CompareProfiles - indicate information of profiles types used
    in calculation.

    :return: Dictionary with alternatives assigned to proper classes
    """
    check_dominance_condition(criteria_directions, category_profiles)

    if comparison_with_profiles == CompareProfiles.LIMITING_PROFILES:
        return _limiting_profiles_sorting(categories, prometheeII_net_flows)
    elif comparison_with_profiles == CompareProfiles.BOUNDARY_PROFILES:
        return _boundary_profiles_sorting(categories, category_profiles, prometheeII_net_flows)
    else:
        return _central_profiles_sorting(categories, category_profiles, prometheeII_net_flows)
