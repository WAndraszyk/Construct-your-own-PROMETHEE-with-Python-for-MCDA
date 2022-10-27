"""
    This class computes positive and negative outranking flows based on preferences.
"""
import pandas as pd
from core.aliases import PreferencesTable, FlowsTable
from typing import Tuple, Union

__all__ = ["calculate_prometheeI_outranking_flows", "calculate_prometheeII_outranking_flows"]


def _calculate_flow(preferences: Union[Tuple[PreferencesTable, PreferencesTable], PreferencesTable],
                    positive: bool = True, prometheeII: bool = True) -> pd.Series:
    """
    Calculate positive or negative outranking flow.

    :param positive: If True function returns positive outranking flow else returns negative outranking flow.
    :return: List of outranking flow's values.
    """
    if isinstance(preferences, tuple):
        if positive:
            flows = preferences[0].mean(axis=1)
        else:
            flows = preferences[1].mean(axis=0)
    else:
        axis = 1 if positive else 0
        aggregated_preferences = preferences.sum(axis=axis)

        if prometheeII:
            n = preferences.shape[0]
            flows = aggregated_preferences / (n - 1)
        else:
            return aggregated_preferences

    return flows


def calculate_prometheeI_outranking_flows(
        preferences: Union[Tuple[PreferencesTable, PreferencesTable], PreferencesTable]) -> FlowsTable:
    """
    Calculate both positive and negative outranking flows for Promethee I method.

    :return: FlowTable of both positive and negative outranking flows.
    """
    index = preferences[0].index if isinstance(preferences, tuple) else preferences.index
    return pd.DataFrame({'positive': _calculate_flow(preferences, prometheeII=False),
                         'negative': _calculate_flow(preferences, positive=False, prometheeII=False)
                         }, index=index)


def calculate_prometheeII_outranking_flows(
        preferences: Union[Tuple[PreferencesTable, PreferencesTable], PreferencesTable]) -> FlowsTable:
    """
    Calculate both positive and negative outranking flows for Promethee II method.

    :return: FlowTable of both positive and negative outranking flows.
    """
    index = preferences[0].index if isinstance(preferences, tuple) else preferences.index
    return pd.DataFrame({'positive': _calculate_flow(preferences),
                         'negative': _calculate_flow(preferences, positive=False)
                         }, index=index)
