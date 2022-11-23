"""
    This module computes the assignments of given alternatives to categories using FlowSort procedure based on
    Promethee II flows.
"""
import pandas as pd
from typing import List
from core.enums import CompareProfiles
from core.aliases import PerformanceTable
from core.input_validation.sorting_input_validation import flow_sort_ii_validation
from core.promethee_check_dominance import check_dominance_condition

__all__ = ["calculate_flowsortII_sorted_alternatives"]


def _limiting_profiles_sorting(categories: List[str], prometheeII_flows: pd.DataFrame) -> pd.DataFrame:
    """
    Comparing positive and negative flows of each alternative with all limiting profiles and assign them to
    correctly class.

    :param categories: List of categories names (strings only)
    :param prometheeII_flows: DataFrame with Promethee II flows

    :return: Series with alternatives classification
    """

    def _assign_alternative_to_class(alternative: str, alternative_flows: pd.Series,
                                     profiles_flows: pd.Series, categories: List[str], flow_type: str):

        for i, (profile, profile_flows) in enumerate(profiles_flows.iterrows()):
            if (alternative_flows[flow_type] <= profile_flows[flow_type] and flow_type in ['positive', 'net']) or \
                    (alternative_flows[flow_type] >= profile_flows[flow_type] and flow_type == 'negative'):
                if i == 0:
                    classification.loc[alternative, flow_type] = "Under limit"
                else:
                    classification.loc[alternative, flow_type] = categories[i - 1]
                break
            elif i == (len(profiles_flows) - 1):
                classification.loc[alternative, flow_type] = "Over limit"

    classification = pd.DataFrame(dtype=str, columns=['positive', 'negative', 'net'])

    for Ralternative, alternative_group_flows in prometheeII_flows.groupby(level=0):
        alternative = Ralternative[1:]
        profiles_flows = alternative_group_flows.iloc[:-1]
        alternative_flows = alternative_group_flows.iloc[-1]

        for flow_type in ['positive', 'negative', 'net']:
            _assign_alternative_to_class(alternative, alternative_flows, profiles_flows, categories, flow_type)

    return classification


def _boundary_profiles_sorting(categories: List[str], prometheeII_flows: pd.DataFrame) -> pd.DataFrame:
    """
    Comparing positive and negative flows of each alternative with all boundary profiles and assign them to
    correctly class.

    :param categories: List of categories names (strings only)
    :param category_profiles: DataFrame with category profiles performances
    :param prometheeII_net_flows: Series with Promethee II net flows

    :return: Series with alternatives classification
    """

    def _assign_alternative_to_class(alternative: str, alternative_flows: pd.Series,
                                     profiles_flows: pd.Series, categories: List[str], flow_type: str):

        for i, (profile, profile_flows) in enumerate(profiles_flows.iterrows()):
            if (alternative_flows[flow_type] <= profile_flows[flow_type] and flow_type in ['positive', 'net']) or \
                    (alternative_flows[flow_type] >= profile_flows[flow_type] and flow_type == 'negative'):
                classification.loc[alternative, flow_type] = categories[i]
                break
            elif i == (len(profiles_flows) - 1):
                classification.loc[alternative, flow_type] = categories[-1]

    classification = pd.DataFrame(dtype=str, columns=['positive', 'negative', 'net'])

    for Ralternative, alternative_group_flows in prometheeII_flows.groupby(level=0):
        alternative = Ralternative[1:]
        profiles_flows = alternative_group_flows.iloc[:-1]
        alternative_flows = alternative_group_flows.iloc[-1]

        for flow_type in ['positive', 'negative', 'net']:
            _assign_alternative_to_class(alternative, alternative_flows, profiles_flows, categories, flow_type)

    return classification


def _central_profiles_sorting(categories: List[str], prometheeII_flows: pd.DataFrame) -> pd.DataFrame:
    """
    Comparing positive and negative flows of each alternative with all central profiles and assign them to
    correctly class.

    :param categories: List of categories names (strings only)
    :param prometheeII_flows: DataFrame with Promethee II net flows

    :return: Series with alternatives classification
    """
    def _assign_alternative_to_class(alternative: str, alternative_flows: pd.Series,
                                     profiles_flows: pd.Series, categories: List[str], flow_type: str):

        for i, (profile, profile_flows) in enumerate(profiles_flows.iterrows()):
            if i == (len(profiles_flows) - 1):
                if (alternative_flows[flow_type] >
                    (profile_flows[flow_type] + profiles_flows.iloc[i - 1][flow_type]) / 2 and
                    flow_type in ['positive', 'net']) or \
                    (alternative_flows[flow_type] <
                     (profile_flows[flow_type] + profiles_flows.iloc[i - 1][flow_type]) / 2 and
                     flow_type == 'negative'):
                    classification.loc[alternative, flow_type] = categories[i]
                classification.loc[alternative, flow_type] = categories[-1]
            else:
                if (alternative_flows[flow_type] <=
                    (profile_flows[flow_type] + profiles_flows.iloc[i + 1][flow_type]) / 2 and
                    flow_type in ['positive', 'net']) or \
                    (alternative_flows[flow_type] >=
                     (profile_flows[flow_type] + profiles_flows.iloc[i + 1][flow_type]) / 2 and
                     flow_type == 'negative'):
                    classification.loc[alternative, flow_type] = categories[i]
                    break

    classification = pd.DataFrame(dtype=str, columns=['positive', 'negative', 'net'])

    for Ralternative, alternative_group_flows in prometheeII_flows.groupby(level=0):
        alternative = Ralternative[1:]
        profiles_flows = alternative_group_flows.iloc[:-1]
        alternative_flows = alternative_group_flows.iloc[-1]

        for flow_type in ['positive', 'negative', 'net']:
            _assign_alternative_to_class(alternative, alternative_flows, profiles_flows, categories, flow_type)

    return classification


def calculate_flowsortII_sorted_alternatives(categories: List[str],
                                             category_profiles: PerformanceTable,
                                             criteria_directions: pd.Series,
                                             prometheeII_flows: pd.DataFrame,
                                             comparison_with_profiles: CompareProfiles) -> pd.DataFrame:
    """
    Sort alternatives to proper categories.

    :param categories: List of categories names (strings only)
    :param category_profiles: DataFrame with category profiles performances
    :param criteria_directions: Series with criteria directions (max or min)
    :param prometheeII_flows: DataFrame with Promethee II flows (positive, negative and net)
    :param comparison_with_profiles: Enum CompareProfiles - indicate information of profiles types used
    in calculation.

    :return: DataFrame with altenatives sorted to proper categories using flows (positive, negative and net)
    """
    flow_sort_ii_validation(categories, category_profiles, criteria_directions, prometheeII_flows,
                            comparison_with_profiles)
    check_dominance_condition(criteria_directions, category_profiles)

    if comparison_with_profiles == CompareProfiles.LIMITING_PROFILES:
        return _limiting_profiles_sorting(categories, prometheeII_flows)
    elif comparison_with_profiles == CompareProfiles.BOUNDARY_PROFILES:
        return _boundary_profiles_sorting(categories, prometheeII_flows)
    else:
        return _central_profiles_sorting(categories, prometheeII_flows)
