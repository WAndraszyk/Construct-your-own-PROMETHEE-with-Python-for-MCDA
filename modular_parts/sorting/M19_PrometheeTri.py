"""
    This module computes the assignments of given alternatives to categories
    using Promethee Tri method.

    Implementation and naming of conventions are taken from
    :cite:p:'FigueiraDeSmetBrans2004' and :cite:p:'ArazOzkarahan2007'.
"""

import pandas as pd
from typing import List, Tuple
from core.promethee_flow import compute_single_criterion_net_flows
from core.input_validation import promethee_tri_validation

__all__ = ["calculate_prometheetri_sorted_alternatives"]


def _calculate_criteria_net_flows(
        alternatives_partial_preferences: Tuple[pd.DataFrame, pd.DataFrame],
        profiles_partial_preferences: pd.DataFrame) -> \
        Tuple[pd.DataFrame, pd.DataFrame]:
    """
    This function calculates criteria net flows for profiles and alternatives.

    :param alternatives_partial_preferences: Tuple with pd.DataFrame with
    alternatives names as index and profiles names as columns and pd.DataFrame
    objects with profiles names as index and alternatives names as columns
    :param profiles_partial_preferences: pd.DataFrame with profiles names as
    index and profiles names as columns

    :return: Tuple with pd.DataFrame with profiles names as index and criteria
    names as columns and pd.DataFrame objects with alternatives names as index
    and criteria names as columns
    """
    profiles_criteria_net_flows = compute_single_criterion_net_flows(
        profiles_partial_preferences)

    alternatives_criteria_net_flows = compute_single_criterion_net_flows(
        alternatives_partial_preferences)

    return profiles_criteria_net_flows, alternatives_criteria_net_flows


def _calculate_deviations(alternatives: List[str],
                          criteria_weights: pd.Series,
                          profiles_criteria_net_flows: pd.DataFrame,
                          alternatives_criteria_net_flows: pd.DataFrame,
                          use_marginal_value: bool = True) -> pd.DataFrame:
    """
    This function calculates deviation for each alternative and each profile.

    :param alternatives: List with alternatives names as strings
    :param criteria_weights: Series with weights of each criterion
    :param profiles_criteria_net_flows: pd.DataFrame with profiles names as
    index and criteria names as columns
    :param alternatives_criteria_net_flows: pd.DataFrame with alternatives
    names as index and criteria names as columns
    :param use_marginal_value: Boolean which describe whether deviation
    should be calculated as absolute value or not

    :return: pd.DataFrame with alternatives as index and profiles as columns
    """

    deviations = pd.DataFrame(columns=profiles_criteria_net_flows.index,
                              index=alternatives, dtype=float)

    for alternative, alternative_row in \
            alternatives_criteria_net_flows.iterrows():
        for profile, profile_row in profiles_criteria_net_flows.iterrows():
            # Check if deviations should be calculated as absolute values
            if use_marginal_value:
                deviations.loc[alternative, profile] = (
                        criteria_weights *
                        abs(alternative_row - profile_row)).sum()
            else:
                deviations.loc[alternative, profile] = (criteria_weights * (
                        alternative_row - profile_row)).sum()

    return deviations


def _assign_alternatives_to_classes_with_minimal_deviation(
        categories: List[str],
        alternatives: List[str], deviations: pd.DataFrame,
        assign_to_better_class: bool = True) -> pd.Series:
    """
    This function assigns every alternative to class with minimal deviation
    for pair alternative, class.

    :param categories: List with categories names as strings
    :param alternatives: List with alternatives names as strings
    :param deviations: pd.DataFrame with alternatives as index and profiles
    as columns
    :param assign_to_better_class: Boolean which describe preference of
    the DM in final alternative assignment if total distance is equal
    cut_point value.

    :return: pd.Series with assignments as values
    """
    classification = pd.Series(index=alternatives, dtype=str)
    for alternative, alternative_row in deviations.iterrows():
        if assign_to_better_class:
            classification[alternative] = categories[alternative_row.argmin()]
        else:
            classification[alternative] = categories[
                alternative_row[::-1].argmin()]

    return classification


def calculate_prometheetri_sorted_alternatives(
        categories: List[str],
        criteria_weights: pd.Series,
        alternatives_partial_preferences: Tuple[pd.DataFrame, pd.DataFrame],
        profiles_partial_preferences: pd.DataFrame,
        assign_to_better_class: bool = True,
        use_marginal_value: bool = True) -> pd.Series:
    """
    This function sorts alternatives to proper categories
    (based on Promethee Tri).

    :param categories: List with categories names as strings
    :param criteria_weights: pd.Series with criterion name as index and weight
    of each criterion as values
    :param alternatives_partial_preferences: Tuple with pd.DataFrame with
    alternatives names as index and profiles names as columns and pd.DataFrame
    objects with profiles names as index and alternatives names as columns
    :param profiles_partial_preferences: pd.DataFrame with profiles names as
    index and profiles names as columns
    :param assign_to_better_class: Boolean which describe preference of
    the DM in final alternative assignment if total distance is equal
    cut_point value.
    :param use_marginal_value: Boolean which describe whether deviation 
    should be calculated as absolute value or not

    :return: pd.Series with assignments as values
    """
    promethee_tri_validation(categories, criteria_weights,
                             alternatives_partial_preferences,
                             profiles_partial_preferences,
                             assign_to_better_class, use_marginal_value)

    alternatives = alternatives_partial_preferences[1].columns.tolist()

    profiles_criteria_net_flows, alternatives_criteria_net_flows = \
        _calculate_criteria_net_flows(alternatives_partial_preferences,
                                      profiles_partial_preferences)

    deviations = _calculate_deviations(alternatives, criteria_weights,
                                       profiles_criteria_net_flows,
                                       alternatives_criteria_net_flows,
                                       use_marginal_value)

    return _assign_alternatives_to_classes_with_minimal_deviation(
        categories, alternatives, deviations, assign_to_better_class)
