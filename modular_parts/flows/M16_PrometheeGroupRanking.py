"""
    This class calculates aggregated flows which are weighted sum of flows for every alternative.
    Allows many Decision Makers to get influence on final flows.
"""
import pandas as pd
from core.input_validation.flow_input_validation import promethee_group_ranking_validation

__all__ = ['calculate_promethee_group_ranking']


def calculate_promethee_group_ranking(dms_flows: pd.DataFrame, dms_weights: pd.Series) -> pd.Series:
    """
    Calculates aggregated flows.

    :param dms_flows: DataFrame with DMs as columns and alternatives as rows
    :param dms_weights: Series with DMs as index and weights as values

    :return: DataFrame with aggregated flows(column 'aggregated') and  weighted flows(column 'weighted')
    """
    promethee_group_ranking_validation(dms_flows, dms_weights)

    weighted_flows = dms_flows.mul(dms_weights, axis=1)
    aggregated_flows = weighted_flows.sum(axis=1)
    aggregated_flows.name = 'aggregated_flows'

    return aggregated_flows
