"""
    This module computes the assignments of given alternatives to categories
     using FlowSort procedure based on Promethee II flows.

    Implementation and naming convention are taken from the
    :cite:p:'NemeryLamboray2007'
"""
import pandas as pd
from typing import List
from core.enums import CompareProfiles
from core.input_validation import flow_sort_ii_validation
from core.promethee_check_dominance import check_dominance_condition

__all__ = ["calculate_flowsortII_sorted_alternatives"]


def _limiting_profiles_sorting(alternative: str,
                               alternative_flows: pd.Series,
                               profiles_flows: pd.Series,
                               categories: List[str],
                               flow_type: str,
                               classification: pd.DataFrame):
    """
    Assign alternative to the category based on the limiting profiles.

    :param alternative: str, alternative name
    :param alternative_flows: pd.Series with alternative as index
    and flows as values
    :param profiles_flows: pd.Series with profiles as index and
    flows as values
    :param categories: List with categories names as strings
    :param flow_type: str, flow type ('positive', 'negative' or 'net')
    :param classification: pd.DataFrame with alternatives as index and
    'positive', 'negative' and 'net' as columns. This object is modified by
    adding new assignment.
    """

    # Iterate over profiles flows until the first profile with better
    # flow is found
    for i, (profile, profile_flows) in enumerate(profiles_flows.iterrows()):
        if (alternative_flows[flow_type] <= profile_flows[flow_type] and
            flow_type in ['positive', 'net']) or \
                (alternative_flows[flow_type] >= profile_flows[flow_type] and
                 flow_type == 'negative'):
            # Edge case: if the first profile is better than the alternative
            if i == 0:
                classification.loc[alternative, flow_type] = "Under limit"
            else:
                classification.loc[alternative, flow_type] = \
                    categories[i - 1]
            break
        # Edge case: if the alternative is better than the last profile
        elif i == (len(profiles_flows) - 1):
            classification.loc[alternative, flow_type] = "Over limit"


def _boundary_profiles_sorting(alternative: str,
                               alternative_flows: pd.Series,
                               profiles_flows: pd.Series,
                               categories: List[str], flow_type: str,
                               classification: pd.DataFrame):
    """
    Assign alternative to the category based on the boundary profiles.

    :param alternative: str, alternative name
    :param alternative_flows: pd.Series with alternative as index
    and flows as values
    :param profiles_flows: pd.Series with profiles as index and
    flows as values
    :param categories: List with categories names as strings
    :param flow_type: str, flow type ('positive', 'negative' or 'net')
    :param classification: pd.DataFrame with alternatives as index and
    'positive', 'negative' and 'net' as columns. This object is modified by
    adding new assignment.
    """

    # Iterate over profiles flows until the first profile
    # with better flow is found
    for i, (profile, profile_flows) in enumerate(profiles_flows.iterrows()):
        if (alternative_flows[flow_type] <= profile_flows[flow_type] and
            flow_type in ['positive', 'net']) or \
                (alternative_flows[flow_type] >= profile_flows[flow_type] and
                 flow_type == 'negative'):
            classification.loc[alternative, flow_type] = categories[i]
            break
        # Edge case: if the alternative is better than the last profile
        elif i == (len(profiles_flows) - 1):
            classification.loc[alternative, flow_type] = categories[-1]


def _central_profiles_sorting(alternative: str,
                              alternative_flows: pd.Series,
                              profiles_flows: pd.Series,
                              categories: List[str],
                              flow_type: str,
                              classification: pd.DataFrame):
    """
    Assign alternative to the category based on the central profiles.

    :param alternative: str, alternative name
    :param alternative_flows: pd.Series with alternative as index
    and flows as values
    :param profiles_flows: pd.Series with profiles as index and
    flows as values
    :param categories: List with categories names as strings
    :param flow_type: str, flow type ('positive', 'negative' or 'net')
    :param classification: pd.DataFrame with alternatives as index and
    'positive', 'negative' and 'net' as columns. This object is modified by
    adding new assignment.
    """

    # Iterate over profiles flows until the first profile with better mean
    # with the next profile is found
    for i, (profile, profile_flows) in enumerate(profiles_flows.iterrows()):
        # Edge case: last alternative is better than last profile
        if i == (len(profiles_flows) - 1):
            if (alternative_flows[flow_type] >
                (profile_flows[flow_type] +
                 profiles_flows.iloc[i - 1][flow_type]) / 2 and
                flow_type in ['positive', 'net']) or \
                    (alternative_flows[flow_type] <
                     (profile_flows[flow_type] +
                      profiles_flows.iloc[i - 1][flow_type]) / 2 and
                     flow_type == 'negative'):
                classification.loc[alternative, flow_type] = categories[i]
            classification.loc[alternative, flow_type] = categories[-1]
        else:
            if (alternative_flows[flow_type] <=
                (profile_flows[flow_type] +
                 profiles_flows.iloc[i + 1][flow_type]) / 2 and
                flow_type in ['positive', 'net']) or \
                    (alternative_flows[flow_type] >=
                     (profile_flows[flow_type] +
                      profiles_flows.iloc[i + 1][flow_type]) / 2 and
                     flow_type == 'negative'):
                classification.loc[alternative, flow_type] = categories[i]
                break


def calculate_flowsortII_sorted_alternatives(
        categories: List[str],
        profiles_performances: pd.DataFrame,
        criteria_directions: pd.Series,
        prometheeII_flows: pd.DataFrame,
        comparison_with_profiles: CompareProfiles) -> pd.DataFrame:
    """
    Sort alternatives to proper categories using FlowSort method
    and Promethee II flows.

    :param categories: List of categories names as strings
    :param profiles_performances: pd.DataFrame with profiles as index
    and criteria as columns
    :param criteria_directions: pd.Series with criteria as index and
    Direction enums as values. Indicates if criterion has to be maximized
    or minimized.
    :param prometheeII_flows: pd.DataFrame with
    MultiIndex("R" + alternatives, profiles + alternative) as index and
    'positive', 'negative' and 'net' columns
    :param comparison_with_profiles: CompareProfiles enum. Indicates if
    type of profiles used in sorting (limiting, boundary or central)
    :return: pd.DataFrame with alternatives as index and
    'positive', 'negative' and 'net' columns. Each column contains
    category name as value.
    """

    # Input validation
    flow_sort_ii_validation(categories, profiles_performances,
                            criteria_directions, prometheeII_flows,
                            comparison_with_profiles)

    # Check dominance condition
    check_dominance_condition(criteria_directions,
                              profiles_performances)

    # Init classification structure
    classification = pd.DataFrame(dtype=str,
                                  columns=['positive', 'negative', 'net'])

    # Iterate over flow groups (profiles + alternative)
    for Ralternative, alternative_group_flows in \
            prometheeII_flows.groupby(level=0):
        # Get alternative name
        alternative = Ralternative[1:]

        # Separate profiles and alternative flows
        profiles_flows = alternative_group_flows.iloc[:-1]
        alternative_flows = alternative_group_flows.iloc[-1]

        # Assign alternative to class using all types of flows
        for flow_type in ['positive', 'negative', 'net']:
            if comparison_with_profiles == CompareProfiles.LIMITING_PROFILES:
                _limiting_profiles_sorting(alternative, alternative_flows,
                                           profiles_flows, categories,
                                           flow_type, classification)
            elif comparison_with_profiles == \
                    CompareProfiles.BOUNDARY_PROFILES:
                _boundary_profiles_sorting(alternative, alternative_flows,
                                           profiles_flows, categories,
                                           flow_type, classification)
            elif comparison_with_profiles == CompareProfiles.CENTRAL_PROFILES:
                _central_profiles_sorting(alternative, alternative_flows,
                                          profiles_flows, categories,
                                          flow_type, classification)

    return classification
