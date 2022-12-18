"""
    This module profile the alternatives using the single criterion net flows.

    Implementation and naming of conventions are taken from
    :cite:p:'BransMareschal2005'.
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

    :param criteria_weights: pd.Series with criterion names as index and
    weight of each criterion as values
    :param criteria_net_flows: pd.DataFrame with alternatives names as index
    and criteria names as columns

    return: pd.Series with alternatives name as index and aggregated net flows
    as values
    """
    not_aggregated_net_flows = criteria_net_flows.mul(criteria_weights)
    net_flows = not_aggregated_net_flows.sum(axis=1)

    return net_flows


def calculate_alternatives_profiles(criteria_weights: pd.Series,
                                    partial_preferences: pd.DataFrame
                                    ) -> pd.Series:
    """
    This function calculates profiles of alternatives.

    :param criteria_weights: pd.Series with criterion name as index and weight
    of each criterion as values
    :param partial_preferences: pd.DataFrame with criteria and alternatives
    names as index and alternatives names as columns

    return: pd.Series with alternatives names as index and alternatives
    profiles as values
    """
    alternatives_profiles_validation(criteria_weights, partial_preferences)

    criteria_net_flows = compute_single_criterion_net_flows(
        partial_preferences)
    net_flows = _calculate_net_flows(criteria_weights, criteria_net_flows)

    return net_flows
