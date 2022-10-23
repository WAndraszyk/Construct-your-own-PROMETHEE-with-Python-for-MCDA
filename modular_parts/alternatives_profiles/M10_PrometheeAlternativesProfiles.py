"""
    This module profile the alternatives using the single criterion net flows.
"""

import pandas as pd
from core.aliases import PreferencesTable

__all__ = ["calculate_alternatives_profiles"]


def _calculate_criteria_net_flows(partial_preferences: PreferencesTable) -> pd.DataFrame:
    """
    Calculate criteria net flows for alternatives.

    :param partial_preferences: DataFrame with MultiIndex of criterion and alternative and alternative as columns.
    return: DataFrame with criteria net flows
    """
    alternatives = partial_preferences.columns.tolist()
    criteria_net_flows = pd.DataFrame()
    n_alternatives = len(alternatives)

    for criterion, criterion_preferences in partial_preferences.groupby(level=0):
        for alternative_i, alternative_i_row, alternative_j, alternative_j_col \
                in zip(criterion_preferences.droplevel(0).iterrows(),
                       criterion_preferences.droplevel(0).T.iterrows()):
            criteria_net_flows[alternative_i] = (alternative_i_row - alternative_j_col) / (n_alternatives - 1)

    criteria_net_flows = criteria_net_flows.T
    criteria_net_flows.columns = partial_preferences.index.get_level_values(0)
    criteria_net_flows.index = alternatives

    return criteria_net_flows


def _calculate_net_flows(criteria_weights: pd.Series, criteria_net_flows: pd.DataFrame) -> pd.Series:
    """
    Aggregate single criterion net flows multiplied by weights of criterion to compute the net outranking flow.

    :param criteria_weights: Series with name as index and weight of each criterion
    :param criteria_net_flows: DataFrame with criteria net flows
    return: Series with aggregated net flows
    """
    not_aggregated_net_flows = criteria_net_flows.mul(criteria_weights)
    net_flows = not_aggregated_net_flows.sum(axis=1)

    return net_flows


def calculate_alternatives_profiles(criteria_weights: pd.Series, partial_preferences: PreferencesTable) -> pd.Series:
    """
    Calculate the alternatives profiles.

    return: Series with alternatives profiles
    """
    criteria_net_flows = _calculate_criteria_net_flows(partial_preferences)
    net_flows = _calculate_net_flows(criteria_weights, criteria_net_flows)

    return net_flows
