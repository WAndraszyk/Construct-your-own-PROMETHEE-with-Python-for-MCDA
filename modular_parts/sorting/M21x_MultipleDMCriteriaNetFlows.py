"""
    Extra module for calculating GDSS flows for FlowSortGDSS.
"""

import pandas as pd
from typing import List, Tuple

__all__ = ["calculate_gdss_flows"]


def _calculate_alternatives_general_net_flows(alternatives: pd.Index, category_profiles: pd.Index,
                                              criteria_weights: pd.Series,
                                              dms_profiles_partial_preferences: List[pd.DataFrame],
                                              dms_alternatives_partial_preferences: List[pd.DataFrame],
                                              dms_profile_vs_profile_partial_preferences: pd.DataFrame) -> pd.Series:
    """
    First calculate net flows for each alternative, each profile and each criterion,
    then accumulate criteria values to global alternative net flows.

    :param alternatives: Index with alternatives names
    :param category_profiles: Index with category profiles names
    :param criteria_weights: Series of numeric value weights for each criterion
    :param dms_profiles_partial_preferences: List of partial preferences profiles vs alternatives.
     MultiIndex: DM, criterion, profile; Column: alternative
    :param dms_alternatives_partial_preferences: List of partial preferences alternatives vs profiles.
     Nesting order: DM, criterion, alternative, profile
    :param dms_profile_vs_profile_partial_preferences: DataFrame with partial preferences profiles vs profiles
     between any DM. Nesting order: DM, criterion, profile_i, profile_j

    :return: Series with global net flows (for each alternative)
    """
    alternatives_net_flows_index = pd.MultiIndex.from_product(
        [dms_profile_vs_profile_partial_preferences.index.get_level_values(0), category_profiles])

    alternatives_net_flows = pd.Series(index=alternatives_net_flows_index, dtype=float)

    n_profiles = len(category_profiles) * len(dms_profiles_partial_preferences)

    for alternatives_partial_preferences, profiles_partial_preferences \
            in zip(dms_alternatives_partial_preferences, dms_profiles_partial_preferences):

        for (criterion, criterion_preferences1, _, criterion_preferences2) \
                in zip(alternatives_partial_preferences.groupby(level=0),
                       profiles_partial_preferences.groupby(level=0)):
            for alternative_i, alternative_i_row, profile_j, profile_j_col \
                    in zip(criterion_preferences1.droplevel(0).iterrows(),
                           criterion_preferences2.droplevel(0).T.iterrows()):
                alternatives_net_flows[(criterion, alternative_i[1])] += (alternative_i_row - profile_j_col)

    alternatives_net_flows /= n_profiles

    alternatives_global_net_flows = pd.Series(index=alternatives, dtype=float)
    for DM_profile, alternative_criteria_net_flows in alternatives_net_flows.groupby(level=[1, 2]):
        alternatives_global_net_flows[DM_profile] = alternative_criteria_net_flows.multiply(
            criteria_weights, axis='rows').sum()

    return alternatives_global_net_flows


def _calculate_profiles_general_net_flows(alternatives: pd.Index, category_profiles: pd.Index,
                                          criteria_weights: pd.Series,
                                          dms_profiles_partial_preferences: List[pd.DataFrame],
                                          dms_alternatives_partial_preferences: List[pd.DataFrame],
                                          dms_profile_vs_profile_partial_preferences: pd.DataFrame) -> pd.DataFrame:
    """
    First calculate net flows for each alternative, each DM, each category profile and each criterion,
    then accumulate criteria values to global profiles net flows.

    :param alternatives: Index with alternatives names
    :param category_profiles: Index with category profiles names
    :param criteria_weights: Series of numeric value weights for each criterion
    :param dms_profiles_partial_preferences: List of partial preferences profiles vs alternatives.
     MultiIndex: DM, criterion, profile; Column: alternative
    :param dms_alternatives_partial_preferences: List of partial preferences alternatives vs profiles.
     Nesting order: DM, criterion, alternative, profile
    :param dms_profile_vs_profile_partial_preferences: DataFrame with partial preferences profiles vs profiles
     between any DM. Nesting order: DM, criterion, profile_i, profile_j

    :return: List of global profiles net flows. Nesting order: alternative, DM, profile
    """
    n_profiles = len(category_profiles) * len(dms_profiles_partial_preferences)

    profiles_vs_profiles = pd.DataFrame(index=dms_profile_vs_profile_partial_preferences.index,
                                        columns=dms_profile_vs_profile_partial_preferences.columns,
                                        dtype=float)

    # group by criterion
    for (criterion, criterion_preferences) in dms_profile_vs_profile_partial_preferences.groupby(level=0):
        for profile_i, profile_i_row, profile_j, profile_j_col \
                in zip(criterion_preferences.droplevel(0).iterrows(),
                       criterion_preferences.droplevel(0).T.iterrows()):
            profiles_vs_profiles.loc[(criterion, *profile_i), profile_j] = profile_i_row - profile_j_col

    profiles_vs_profiles_sum = profiles_vs_profiles.sum(axis=1)

    alternatives_vs_profiles = pd.DataFrame(index=dms_profile_vs_profile_partial_preferences.index,
                                            columns=alternatives)

    for alternatives_partial_preferences, profiles_partial_preferences \
            in zip(dms_alternatives_partial_preferences, dms_profiles_partial_preferences):

        for (criterion, criterion_preferences1, _, criterion_preferences2) \
                in zip(profiles_partial_preferences.groupby(level=0),
                       alternatives_partial_preferences.groupby(level=0)):
            for profile_i, profile_i_row, alternative_j, alternative_j_col \
                    in zip(criterion_preferences1.droplevel(0).iterrows(),
                           criterion_preferences2.droplevel(0).T.iterrows()):
                alternatives_vs_profiles[(criterion, *profile_i), alternative_j[1]] = \
                    profile_i_row - alternative_j_col

    profiles_criteria_net_flows = alternatives_vs_profiles.apply(lambda col:
                                                                 (col + profiles_vs_profiles_sum) / n_profiles)

    profiles_global_net_flows_index = profiles_criteria_net_flows.droplevel(0).index.unique()

    profiles_global_net_flows = pd.DataFrame(index=profiles_global_net_flows_index, columns=alternatives)
    for DM_profile, profile_criteria_net_flows in profiles_criteria_net_flows.groupby(level=[1, 2]):
        profiles_global_net_flows.loc[DM_profile, :] = profile_criteria_net_flows.multiply(criteria_weights,
                                                                                           axis='rows').sum()

    return profiles_global_net_flows


def calculate_gdss_flows(dms_profiles_partial_preferences: List[pd.DataFrame],  # P(r,a)
                         dms_alternatives_partial_preferences: List[pd.DataFrame],  # P(a,r)
                         dms_profile_vs_profile_partial_preferences: pd.DataFrame,  # P(r_i,r_j)
                         criteria_weights: pd.Series) -> Tuple[pd.Series, pd.DataFrame]:
    """
    Calculate alternatives general net flows and profiles general net flows which are necessary
    in FlowSortGDSS method.

    :param dms_profiles_partial_preferences: List of partial preferences profiles vs alternatives.
     MultiIndex: DM, criterion, profile; Column: alternative
    :param dms_alternatives_partial_preferences: List of partial preferences alternatives vs profiles.
     Nesting order: DM, criterion, alternative, profile
    :param dms_profile_vs_profile_partial_preferences: DataFrame with partial preferences profiles vs profiles
     between any DM. Nesting order: DM, criterion, profile_i, profile_j
    :param criteria_weights: List of numeric value weights for each criterion

    :return: alternatives general net flows(List of net flows for each alternative) \
    and profiles general net flows(3D List of net flows for each alternative, DM and category_profile)
    """
    alternatives = dms_profiles_partial_preferences[0].columns
    category_profiles = dms_alternatives_partial_preferences[0].columns

    alternatives_general_net_flows = \
        _calculate_alternatives_general_net_flows(alternatives, category_profiles,
                                                  criteria_weights, dms_profiles_partial_preferences,
                                                  dms_alternatives_partial_preferences,
                                                  dms_profile_vs_profile_partial_preferences)
    profiles_general_net_flows = _calculate_profiles_general_net_flows(alternatives, category_profiles,
                                                                       criteria_weights,
                                                                       dms_profiles_partial_preferences,
                                                                       dms_alternatives_partial_preferences,
                                                                       dms_profile_vs_profile_partial_preferences)

    return alternatives_general_net_flows, profiles_general_net_flows
