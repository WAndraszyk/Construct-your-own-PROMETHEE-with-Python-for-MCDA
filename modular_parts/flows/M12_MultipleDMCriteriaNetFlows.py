"""
    Extra module for calculating GDSS flows for FlowSortGDSS.
"""

import pandas as pd
from typing import List, Tuple

__all__ = ["calculate_gdss_flows"]

from core.input_validation import multiple_dm_criteria_net_flows_validation


def _calculate_alternatives_general_net_flows(
        alternatives: pd.Index,
        category_profiles: pd.Index,
        criteria_weights: pd.Series,
        dms_profiles_partial_preferences: List[pd.DataFrame],
        dms_alternatives_partial_preferences: List[
            pd.DataFrame]) -> pd.Series:
    """
    First calculate net flows for each alternative, each profile
    and each criterion,
    then accumulate criteria values to global alternative net flows.

    :param alternatives: Index with alternatives names
    :param category_profiles: Index with category profiles names
    :param criteria_weights: Series of numeric value weights for each
    criterion
    :param dms_profiles_partial_preferences: List of partial preferences
    profiles vs alternatives.
     MultiIndex: DM, criterion, profile; Column: alternative
    :param dms_alternatives_partial_preferences: List of partial preferences
    alternatives vs profiles.
     Nesting order: DM, criterion, alternative, profile

    :return: Series with global net flows (for each alternative)
    """
    alternatives_net_flows = pd.DataFrame(index=alternatives,
                                          columns=criteria_weights.index,
                                          dtype=float).fillna(0)

    n_profiles = len(category_profiles) * len(
        dms_profiles_partial_preferences)

    for alternatives_partial_preferences, profiles_partial_preferences \
            in zip(dms_alternatives_partial_preferences,
                   dms_profiles_partial_preferences):

        for (criterion, criterion_preferences1), (_, criterion_preferences2) \
                in zip(alternatives_partial_preferences.groupby(level=0),
                       profiles_partial_preferences.groupby(level=0)):
            for (alternative_i, alternative_i_row), \
                (profile_j, profile_j_col) \
                    in zip(criterion_preferences1.droplevel(0).iterrows(),
                           criterion_preferences2.droplevel(0).T.iterrows()):
                alternatives_net_flows.loc[alternative_i, criterion] += (
                        alternative_i_row - profile_j_col).sum()
    alternatives_net_flows /= n_profiles

    alternatives_global_net_flows = alternatives_net_flows.mul(
        criteria_weights, axis=1).sum(axis=1)

    return alternatives_global_net_flows


def _calculate_profiles_general_net_flows(
        alternatives: pd.Index,
        category_profiles: pd.Index,
        criteria_weights: pd.Series,
        dms_profiles_partial_preferences:
        List[pd.DataFrame],
        dms_alternatives_partial_preferences:
        List[pd.DataFrame],
        dms_profile_vs_profile_partial_preferences: pd.DataFrame
) -> pd.DataFrame:
    """
    First calculate net flows for each alternative, each DM, each category 
    profile and each criterion,
    then accumulate criteria values to global profiles net flows.

    :param alternatives: Index with alternatives names
    :param category_profiles: Index with category profiles names
    :param criteria_weights: Series of numeric value weights for each 
    criterion
    :param dms_profiles_partial_preferences: List of partial preferences 
    profiles vs alternatives.
     MultiIndex: DM, criterion, profile; Column: alternative
    :param dms_alternatives_partial_preferences: List of partial preferences
     alternatives vs profiles.
     Nesting order: DM, criterion, alternative, profile
    :param dms_profile_vs_profile_partial_preferences: DataFrame with partial 
    preferences profiles vs profiles
     between any DM. Nesting order: DM, criterion, profile_i, profile_j

    :return: List of global profiles net flows. Nesting order: alternative, 
    DM, profile
    """
    n_profiles = len(category_profiles) * len(
        dms_profiles_partial_preferences)

    dms = dms_profile_vs_profile_partial_preferences.index.get_level_values(
        1).unique()

    profiles_vs_profiles_sum_index = pd.MultiIndex.from_product([
        dms_profile_vs_profile_partial_preferences.index.get_level_values(
            1).unique(), category_profiles])

    profiles_vs_profiles_sum = pd.DataFrame(
        index=profiles_vs_profiles_sum_index,
        columns=criteria_weights.index,
        dtype=float)

    for (criterion,
         criterion_preferences) in \
            dms_profile_vs_profile_partial_preferences.groupby(level=0):
        for (profile_i, profile_i_row), (profile_j, profile_j_col) \
                in zip(criterion_preferences.droplevel(0).iterrows(),
                       criterion_preferences.droplevel(0).T.iterrows()):
            profiles_vs_profiles_sum.loc[profile_i, criterion] = (
                    profile_i_row - profile_j_col).sum()

    profiles_flows = pd.DataFrame(
        index=dms_profile_vs_profile_partial_preferences.index,
        columns=alternatives)

    for alternatives_partial_preferences, profiles_partial_preferences, dm \
            in zip(dms_alternatives_partial_preferences,
                   dms_profiles_partial_preferences, dms):

        for (criterion, alternatives_vs_profiles_partial_preferences), \
            (_, profiles_vs_alternatives_partial_preferences) in zip(
            alternatives_partial_preferences.groupby(level=0),
            profiles_partial_preferences.groupby(level=0)):
            for (alternative_i, alternative_i_row), (_, profile_j_col) \
                    in zip(
                alternatives_vs_profiles_partial_preferences.droplevel(
                    0).iterrows(),
                profiles_vs_alternatives_partial_preferences.
                        T.iterrows()):
                for (_, alternative_vs_profile_partial_preference), \
                    (criterion_and_profile,
                     profile_vs_alternative_partial_preference) \
                        in zip(alternative_i_row.items(),
                               profile_j_col.items()):
                    profile = criterion_and_profile[1]
                    profiles_flows.loc[
                        (criterion, dm, profile), alternative_i] = \
                        (
                                alternative_vs_profile_partial_preference -
                                profile_vs_alternative_partial_preference +
                                profiles_vs_profiles_sum.loc[
                                    (dm, profile), criterion]) / (
                                n_profiles + 1)

    profiles_global_net_flows_index = pd.MultiIndex.from_product(
        [dms, category_profiles])
    profiles_global_net_flows = pd.DataFrame(
        index=profiles_global_net_flows_index, dtype=float)

    for DM_profile, profile_criteria_net_flows in profiles_flows.groupby(
            level=[1, 2]):
        profiles_global_net_flows.loc[
            DM_profile, alternatives] = profile_criteria_net_flows. \
            reset_index(drop=True) \
            .multiply(criteria_weights.reset_index(drop=True), axis=0).sum(
            axis=0)

    return profiles_global_net_flows


def calculate_gdss_flows(
        dms_partial_preferences: List[Tuple[pd.DataFrame, pd.DataFrame]],
        dms_profile_vs_profile_partial_preferences: pd.DataFrame,
        # P(r_i,r_j)
        criteria_weights: pd.Series) -> Tuple[pd.Series, pd.DataFrame]:
    """
    Calculate alternatives general net flows and profiles general net flows
    which are necessary
    in FlowSortGDSS method.
    :param dms_partial_preferences: List of partial preferences alternatives
    vs preferences.
    :param dms_profile_vs_profile_partial_preferences: DataFrame with partial
    preferences profiles vs profiles
     between any DM. Nesting order: DM, criterion, profile_i, profile_j
    :param criteria_weights: List of numeric value weights for each criterion

    :return: alternatives general net flows(List of net flows for each
     alternative) and profiles general net flows(3D List of net flows for
     each alternative, DM and category_profile)
    """
    dms_alternatives_partial_preferences, dms_profiles_partial_preferences = \
        zip(*dms_partial_preferences)
    dms_profiles_partial_preferences = list(dms_profiles_partial_preferences)
    dms_alternatives_partial_preferences = list(
        dms_alternatives_partial_preferences)

    multiple_dm_criteria_net_flows_validation(
        dms_profiles_partial_preferences,
        dms_alternatives_partial_preferences,
        dms_profile_vs_profile_partial_preferences,
        criteria_weights)

    alternatives = dms_profiles_partial_preferences[0].columns
    category_profiles = dms_alternatives_partial_preferences[0].columns

    alternatives_general_net_flows = \
        _calculate_alternatives_general_net_flows(
            alternatives,
            category_profiles,
            criteria_weights,
            dms_profiles_partial_preferences,
            dms_alternatives_partial_preferences)
    profiles_general_net_flows = _calculate_profiles_general_net_flows(
        alternatives, category_profiles,
        criteria_weights,
        dms_profiles_partial_preferences,
        dms_alternatives_partial_preferences,
        dms_profile_vs_profile_partial_preferences)

    return alternatives_general_net_flows, profiles_general_net_flows
