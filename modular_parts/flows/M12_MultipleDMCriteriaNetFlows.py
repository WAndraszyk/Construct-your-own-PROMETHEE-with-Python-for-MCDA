"""
    Extra module for calculating GDSS flows for FlowSortGDSS.

    Implementation and naming conventions are taken from
    :cite:p:'LoliiIshizakaGamberiniRiminiMessori2015'
"""

import pandas as pd
from typing import List, Tuple

__all__ = ["calculate_gdss_flows"]

from core.input_validation import net_flows_for_multiple_DM_validation


def _calculate_alternatives_general_net_flows(
        alternatives: pd.Index,
        category_profiles: pd.Index,
        criteria_weights: pd.Series,
        dms_profiles_partial_preferences: List[pd.DataFrame],
        dms_alternatives_partial_preferences: List[
            pd.DataFrame]) -> pd.Series:
    """
    First calculate net flows for each alternative for each criterion
    then accumulate flows for each criterion to
    general alternatives net flows.

    :param alternatives: pd.Index with alternatives names
    :param category_profiles: pd.Index with profiles names
    :param criteria_weights: pd.Series with criteria as index and
    criteria weights as values
    :param dms_profiles_partial_preferences: List of pd.DataFrames with
    MultiIndex(criteria, profiles) as index and alternatives as columns.
    :param dms_alternatives_partial_preferences: List of pd.DataFrames with
    MultiIndex(criteria, alternatives) as index and profiles as columns.
    :return: pd.Series with alternatives as index and
    alternatives general net flows as values
    """

    # Init not accumulated (criteria separated) flows
    alternatives_net_flows = pd.DataFrame(index=alternatives,
                                          columns=criteria_weights.index,
                                          dtype=float).fillna(0)

    # Get number of all profiles (n_profiles * n_DMs)
    n_profiles = len(category_profiles) * len(
        dms_profiles_partial_preferences)

    # Iterate simultaneously over alternatives vs profiles
    # and profiles vs alternatives preferences (In fact we are getting
    # preferences of single decision maker)
    for alternatives_partial_preferences, profiles_partial_preferences \
            in zip(dms_alternatives_partial_preferences,
                   dms_profiles_partial_preferences):
        # Extract alternatives vs profiles and
        # profiles vs alternatives preferences on a single criterion
        for (criterion, criterion_preferences1), (_, criterion_preferences2) \
                in zip(alternatives_partial_preferences.groupby(level=0),
                       profiles_partial_preferences.groupby(level=0)):
            # Transpose profiles vs alternatives preferences
            # to get preferences where profiles are preferred
            # to current alternative
            for (alternative_i, alternative_i_row), \
                (profile_j, profile_j_col) \
                    in zip(criterion_preferences1.droplevel(0).iterrows(),
                           criterion_preferences2.droplevel(0).T.iterrows()):
                alternatives_net_flows.loc[alternative_i, criterion] += \
                    (alternative_i_row - profile_j_col).sum()
    # Divide by number of all profiles
    alternatives_net_flows /= n_profiles

    # Multiply flows of criteria by proper criteria and sum them up
    alternatives_global_net_flows = alternatives_net_flows.mul(
        criteria_weights, axis=1).sum(axis=1)

    return alternatives_global_net_flows


def _calculate_profiles_general_net_flows(
        alternatives: pd.Index,
        category_profiles: pd.Index,
        criteria_weights: pd.Series,
        dms_profiles_partial_preferences: List[pd.DataFrame],
        dms_alternatives_partial_preferences: List[pd.DataFrame],
        dms_profile_vs_profile_partial_preferences: pd.DataFrame) \
        -> pd.DataFrame:
    """
    First calculate net flows for each alternative, each DM, each category 
    profile and each criterion,
    then accumulate criteria values to global profiles net flows.

    :param alternatives: pd.Index with alternatives names
    :param category_profiles: pd.Index with profiles names
    :param criteria_weights: pd.Series with criteria as index and
    criteria weights as values
    :param dms_profiles_partial_preferences: List of pd.DataFrames with
    MultiIndex(criteria, profiles) as index and alternatives as columns.
    :param dms_alternatives_partial_preferences: List of pd.DataFrames with
    MultiIndex(criteria, alternatives) as index and profiles as columns.
    :param dms_profile_vs_profile_partial_preferences: pd.DataFrame with
    MultiIndex(criteria, DMs, profiles) as index and MultiIndex(DMs, profiles)
     as columns. This is partial preferences calculated in
     sum of decision maker profiles sets
    :return: pd.DataFrame with MultiIndex(DMs, profiles) as index and
    alternatives as columns
    """

    # Get number of all profiles (n_profiles * n_DMs)
    n_profiles = len(category_profiles) * len(
        dms_profiles_partial_preferences)

    # Get DMs names
    dms = dms_profile_vs_profile_partial_preferences.index.get_level_values(
        1).unique()

    # Get profiles names (assuming that all DMs have the same profiles names)
    profiles = dms_profile_vs_profile_partial_preferences.index. \
        get_level_values(1).unique()

    # To simplify calculations first we accumulate preferences
    # between profiles, because it is some kind of core of formula

    # Prepare proper index for "core"
    profiles_vs_profiles_sum_index = pd.MultiIndex. \
        from_product([profiles, category_profiles])

    # Init not structure to save accumulated profiles vs profiles preferences
    profiles_vs_profiles_sum = pd.DataFrame(
        index=profiles_vs_profiles_sum_index,
        columns=criteria_weights.index,
        dtype=float)

    # Iterate over criteria
    for (criterion, criterion_preferences) in \
            dms_profile_vs_profile_partial_preferences.groupby(level=0):

        # Transpose profiles vs profiles preferences
        # to get preferences where profiles are preferred
        # to current profile (to simplify calculations)
        for (profile_i, profile_i_row), (profile_j, profile_j_col) \
                in zip(criterion_preferences.droplevel(0).iterrows(),
                       criterion_preferences.droplevel(0).T.iterrows()):
            profiles_vs_profiles_sum.loc[profile_i, criterion] = (
                    profile_i_row - profile_j_col).sum()

    # Init profiles net flows for each criterion
    profiles_flows = pd.DataFrame(
        index=dms_profile_vs_profile_partial_preferences.index,
        columns=alternatives)

    # Iterate simultaneously over alternatives vs profiles
    # and profiles vs alternatives preferences and DM names(In fact we are
    # getting preferences and name of single decision maker)
    for alternatives_partial_preferences, profiles_partial_preferences, dm \
            in zip(dms_alternatives_partial_preferences,
                   dms_profiles_partial_preferences, dms):

        # Extract alternatives vs profiles and
        # profiles vs alternatives preferences on a single criterion
        for (criterion, alternatives_vs_profiles_partial_preferences), \
            (_, profiles_vs_alternatives_partial_preferences) in \
                zip(alternatives_partial_preferences.groupby(level=0),
                    profiles_partial_preferences.groupby(level=0)):

            # Transpose profiles vs alternatives preferences
            # to get preferences where profiles are preferred
            # to current alternative
            for (alternative_i, alternative_i_row), (_, profile_j_col) in \
                    zip(
                    alternatives_vs_profiles_partial_preferences.droplevel(
                        0).iterrows(),
                    profiles_vs_alternatives_partial_preferences.T.iterrows(

                    )):

                # Iterate simultaneously over above preferences to get
                # a pair of preferences for each profile
                for (_, alternative_vs_profile_partial_preference), \
                    (criterion_and_profile,
                     profile_vs_alternative_partial_preference) \
                        in zip(alternative_i_row.items(),
                               profile_j_col.items()):
                    # Get profile from index
                    profile = criterion_and_profile[1]

                    # Add the difference of the listed pairs to the "core"
                    # and divide by the number of all profiles
                    # to get the general net flow profiles, but still
                    # not cumulative after the criteria
                    profiles_flows.loc[(criterion, dm, profile),
                                       alternative_i] = \
                        (alternative_vs_profile_partial_preference -
                         profile_vs_alternative_partial_preference +
                         profiles_vs_profiles_sum.loc[(dm, profile),
                                                      criterion]) / \
                        (n_profiles + 1)

    # Create index for output
    profiles_global_net_flows_index = pd.MultiIndex.from_product(
        [dms, category_profiles])

    # Init output structure
    profiles_global_net_flows = pd.DataFrame(
        index=profiles_global_net_flows_index, dtype=float)

    # Multiply flows of criteria by proper criteria and sum them up
    for DM_profile, profile_criteria_net_flows in \
            profiles_flows.groupby(level=[1, 2]):
        profiles_global_net_flows.loc[DM_profile, alternatives] = \
            profile_criteria_net_flows.reset_index(drop=True) \
            .multiply(criteria_weights.reset_index(drop=True), axis=0) \
            .sum(axis=0)

    return profiles_global_net_flows


def calculate_gdss_flows(
        dms_partial_preferences: List[Tuple[pd.DataFrame, pd.DataFrame]],
        dms_profile_vs_profile_partial_preferences: pd.DataFrame,
        criteria_weights: pd.Series) -> Tuple[pd.Series, pd.DataFrame]:
    """
    Calculate alternatives general net flows and profiles general net flows
    which are necessary
    in FlowSortGDSS method.

    :param dms_partial_preferences: List of tuples with pd.DataFrame
    with MultiIndex(criteria, alternatives) as index and profiles as columns
    and pd.DataFrame with MultiIndex(criteria, profiles) as index and
    alternatives as columns. Each tuple stands for one decision maker.
    :param dms_profile_vs_profile_partial_preferences: pd.DataFrame with
    MultiIndex(criteria, DMs, profiles) as index and MultiIndex(DMs, profiles)
     as columns. This is partial preferences calculated in
     sum of decision maker profiles sets
    :param criteria_weights: pd.Series with criteria as index and
    criteria weights as values.
    :return: Tuple with pd.Series with alternatives as index and alternatives
    general net flows as values and pd.DataFrame with
    MultiIndex(DMs, profiles) as index and alternatives as columns.
    This pd.DataFrame contains profiles general net flows.
    """

    # Spilt alternatives vs profiles and profiles vs alternatives preferences
    dms_alternatives_partial_preferences, dms_profiles_partial_preferences = \
        zip(*dms_partial_preferences)
    dms_profiles_partial_preferences = list(dms_profiles_partial_preferences)
    dms_alternatives_partial_preferences = list(
        dms_alternatives_partial_preferences)

    # Input validation
    net_flows_for_multiple_DM_validation(
        dms_profiles_partial_preferences,
        dms_alternatives_partial_preferences,
        dms_profile_vs_profile_partial_preferences,
        criteria_weights)

    # Save alternatives and profiles
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
