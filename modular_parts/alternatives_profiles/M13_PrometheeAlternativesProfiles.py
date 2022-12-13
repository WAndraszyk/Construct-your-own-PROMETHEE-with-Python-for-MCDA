"""
    This module profile the alternatives using the single criterion net flows.
"""

import pandas as pd
from core.promethee_flow import compute_single_criterion_net_flows
from core.input_validation import *

__all__ = ["calculate_alternatives_profiles"]


def _calculate_net_flows(criteria_weights: pd.Series,
                         criteria_net_flows: pd.DataFrame) -> pd.Series:
    """
    Aggregate single criterion net flows multiplied by weights of criterion
    to compute the net outranking flow.

    :param criteria_weights: Series with name as index and weight
    of each criterion
    :param criteria_net_flows: DataFrame with criteria net flows
    return: Series with aggregated net flows
    """
    not_aggregated_net_flows = criteria_net_flows.mul(criteria_weights)
    net_flows = not_aggregated_net_flows.sum(axis=1)

    return net_flows


def calculate_alternatives_profiles(criteria_weights: pd.Series,
                                    partial_preferences: pd.DataFrame
                                    ) -> pd.Series:
    """
    Calculate the alternatives profiles.

    return: Series with alternatives profiles
    """
    alternatives_profiles_validation(criteria_weights, partial_preferences)

    criteria_net_flows = compute_single_criterion_net_flows(
        partial_preferences)
    net_flows = _calculate_net_flows(criteria_weights, criteria_net_flows)

    return net_flows
