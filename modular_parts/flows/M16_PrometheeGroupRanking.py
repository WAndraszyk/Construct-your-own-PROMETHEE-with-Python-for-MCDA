"""
    This class calculates aggregated flows which are weighted sum of flows for every alternative.
    Allows many Decision Makers to get influence on final flows.
"""
import pandas as pd
import numpy as np
from core.aliases import DMsTable

__all__ = ['calculate_promethee_group_ranking']


def _calculate_weighted_flows(dms_data: DMsTable) -> np.ndarray:
    """
    Calculates weighted flows by multiplying flows by each DM weight.
    :return: ndarray(2 dim) of weighted flows
    """
    return np.multiply(dms_data['weights'], dms_data[dms_data.columns.difference(['weights'])].T).T


def calculate_promethee_group_ranking(dms_data: DMsTable) -> pd.DataFrame:
    """
    Calculates aggregated flows.

    :param dms_data: DMsTable of DMs flows (positive or negative) and weights values.

    :return: DataFrame with aggregated flows(column 'aggregated') and  weighted flows(column 'weighted')
    """
    dms_data = dms_data.T

    alternatives = dms_data.index
    weighted_flows = _calculate_weighted_flows(dms_data)
    aggregated_flows = np.sum(weighted_flows, axis=0)

    return pd.DataFrame([weighted_flows, aggregated_flows], columns=['weighted', 'aggregated'], index=alternatives)
