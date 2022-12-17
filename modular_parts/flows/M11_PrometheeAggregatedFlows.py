"""
    This class calculates aggregated flows which are weighted sum of flows
    for every alternative.
    Allows many Decision Makers to get influence on final flows.
"""
import pandas as pd
from core.input_validation import promethee_group_ranking_validation

__all__ = ['calculate_promethee_aggregated_flows']


def calculate_promethee_aggregated_flows(dms_flows: pd.DataFrame,
                                         dms_weights: pd.Series) -> pd.Series:
    """
    This function calculates Promethee aggregated flows.

    :param dms_flows: pd.DataFrame with alternatives names as index and DMs
    as columns
    :param dms_weights: pd.Series with DMs as index and weights as values

    :return: pd.Series with alternatives names as index and aggregated flows
    as values
    """
    promethee_group_ranking_validation(dms_flows, dms_weights)

    weighted_flows = dms_flows.mul(dms_weights, axis=1)
    aggregated_flows = weighted_flows.sum(axis=1)

    return aggregated_flows
