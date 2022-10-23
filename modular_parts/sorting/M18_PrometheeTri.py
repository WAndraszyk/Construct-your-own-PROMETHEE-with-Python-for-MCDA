"""
    This module computes the assignments of given alternatives to categories using Promethee Tri method.
"""

import pandas as pd
from typing import List, Tuple

__all__ = ["calculate_prometheetri_sorted_alternatives"]


def _calculate_criteria_net_flows(alternatives: List[str],
                                  alternatives_partial_preferences: Tuple[pd.DataFrame, pd.DataFrame],
                                  profiles_partial_preferences: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculate criteria net flows for profiles and alternatives.

    :param alternatives: List of alternatives (strings only)
    :param alternatives_partial_preferences: Tuple with 2 DataFrames with partial preferences
    (alternatives vs profiles and profiles vs alternatives)
    :param profiles_partial_preferences: DataFrame with partial preferences (profiles vs profiles)

    :return: Tuple with 2 DataFrames with criteria net flows for profiles and alternatives
    """
    profiles_criteria_net_flows = pd.DataFrame()
    alternatives_criteria_net_flows = pd.DataFrame()

    category_profiles = profiles_partial_preferences.columuns.to_list()
    n_profiles = len(category_profiles)

    for criterion, criterion_preferences in profiles_partial_preferences.groupby(level=0):
        for profile_i, profile_i_row, profile_j, profile_j_col \
                in zip(criterion_preferences.droplevel(0).iterrows(),
                       criterion_preferences.droplevel(0).T.iterrows()):
            profiles_criteria_net_flows[profile_i] = (profile_i_row - profile_j_col) / (n_profiles - 1)

    profiles_criteria_net_flows = profiles_criteria_net_flows.T
    profiles_criteria_net_flows.columns = profiles_partial_preferences.index.get_level_values(0)
    profiles_criteria_net_flows.index = alternatives

    n_alternatives = len(alternatives)

    for (criterion, criterion_preferences1, criterion, criterion_preferences2) \
            in zip(alternatives_partial_preferences[0].groupby(level=0),
                   alternatives_partial_preferences[0].groupby(level=0)):
        for alternative_i, alternative_i_row, profile_j, profile_j_col \
                in zip(criterion_preferences1.droplevel(0).iterrows(),
                       criterion_preferences2.droplevel(0).T.iterrows()):
            alternatives_criteria_net_flows[alternative_i] = (alternative_i_row - profile_j_col) / n_alternatives

    alternatives_criteria_net_flows = alternatives_criteria_net_flows.T
    alternatives_criteria_net_flows.columns = alternatives_partial_preferences[0].index.get_level_values(0)
    alternatives_criteria_net_flows.index = alternatives

    return profiles_criteria_net_flows, alternatives_criteria_net_flows


def _calculate_deviations(alternatives: List[str], profiles_partial_preferences: pd.DataFrame,
                          criteria_weights: pd.Series, profiles_criteria_net_flows: pd.DataFrame,
                          alternatives_criteria_net_flows: pd.DataFrame,
                          use_marginal_value: bool = True) -> pd.DataFrame:
    """
    Calculate deviation for each alternative and each profile.

    :param alternatives: List of alternatives (strings only)
    :param profiles_partial_preferences: DataFrame with partial preferences (profiles vs profiles)
    :param criteria_weights: Series with weights of each criterion
    :param profiles_criteria_net_flows: DataFrame with criteria net flows for profiles
    :param alternatives_criteria_net_flows: DataFrame with criteria net flows for alternatives
    :param use_marginal_value: Boolean which describe whether deviation should be calculated as absolute value or not

    :return: DataFrame with deviations
    """

    deviations = pd.DataFrame(columns=profiles_partial_preferences.index, index=alternatives)

    for alternative, alternative_row in alternatives_criteria_net_flows.iterrows():
        for profile, profile_row in profiles_criteria_net_flows.iterrows():
            if use_marginal_value:
                deviations[profile][alternative] = abs(alternative_row - profile_row).sum()
            else:
                deviations[profile][alternative] = (criteria_weights * (alternative_row - profile_row)).sum()

    return deviations


def _assign_alternatives_to_classes_with_minimal_deviation(alternatives: List[str], deviations: pd.DataFrame,
                                                           assign_to_better_class: bool = True) -> pd.Series:
    """
    Assign every alternative to class with minimal deviation for pair alternative, class.

    :param alternatives: List of alternatives (strings only)
    :param deviations: DataFrame with deviations
    :param assign_to_better_class: Boolean which describe preference of the DM in final alternative assignment when
    deviation for two or more profiles are the same.

    :return: Series with precise assignments of alternatives to categories
    """
    classification = pd.Series(index=alternatives)
    for alternative, alternative_row in deviations.iterrows():
        if assign_to_better_class:
            classification[alternative] = alternative_row.contains(alternative_row.min()).idxmax()
        else:
            classification[alternative] = alternative_row.contains(alternative_row.min()).idxmin()

    return classification


def calculate_prometheetri_sorted_alternatives(criteria_weights: pd.Series,
                                               alternatives_partial_preferences: Tuple[pd.DataFrame, pd.DataFrame],
                                               profiles_partial_preferences: pd.DataFrame,
                                               assign_to_better_class: bool = True,
                                               use_marginal_value: bool = True) -> pd.Series:
    """
    Sort alternatives to proper categories.

    :param criteria_weights: Series with weights of each criterion
    :param alternatives_partial_preferences: Tuple with 2 DataFrames with partial preferences (alternatives vs profiles
    and profiles vs alternatives)
    :param profiles_partial_preferences: DataFrame with partial preferences (profiles vs profiles)
    :param assign_to_better_class: Boolean which describe preference of the DM in final alternative assignment when
    deviation for two or more profiles are the same.
    :param use_marginal_value: Boolean which describe whether deviation should be
    calculated as absolute value or not

    :return: Series with precise assignments of alternatives to categories
    """
    alternatives = alternatives_partial_preferences[1].columns.tolist()

    profiles_criteria_net_flows, alternatives_criteria_net_flows = \
        _calculate_criteria_net_flows(alternatives, alternatives_partial_preferences, profiles_partial_preferences)
    deviations = _calculate_deviations(alternatives, profiles_partial_preferences, criteria_weights,
                                       profiles_criteria_net_flows, alternatives_criteria_net_flows, use_marginal_value)
    return _assign_alternatives_to_classes_with_minimal_deviation(alternatives, deviations, assign_to_better_class)
