from enum import Enum

import pandas as pd

__all__ = ["promethee_i_ranking_validation", "promethee_iii_ranking_validation", "net_flow_score_iterative_validation",
           "promethee_ii_ranking_validation"]

from core.aliases import NumericValue
# M11
from core.input_validation.flow_input_validation import net_flow_score_validation, _check_flows
from core.input_validation.preference_input_validation import _check_decimal_place, _check_if_dataframe


def _check_weak_preference(weak_pref: bool):
    if not isinstance(weak_pref, bool):
        raise ValueError("Weak preference parameter should have value True or False")


def _check_net_flowsII(net_flows: pd.DataFrame):
    if not isinstance(net_flows, pd.DataFrame):
        raise TypeError(f"Net Flows should be passed as a DataFrame object")
    if 'net' not in net_flows.columns:
        raise ValueError(f'No "net" flow in given DataFrame columns')
    if net_flows['net'].dtype not in ['int64', 'float64']:
        raise ValueError(f"Net Flow should be passed with numeric values")


def promethee_ii_ranking_validation(net_flow: pd.DataFrame):
    _check_net_flowsII(net_flow)


def promethee_i_ranking_validation(flows: pd.DataFrame, weak_preference: bool):
    _check_flows(flows)
    _check_weak_preference(weak_preference)


def net_flow_score_iterative_validation(alternative_preferences: pd.DataFrame, function: Enum,
                                        direction: Enum, avoid_same_scores: bool):
    net_flow_score_validation(alternative_preferences, function, direction, avoid_same_scores)


def _check_alpha(alpha: NumericValue):
    if not isinstance(alpha, (int, float)):
        raise TypeError("Alpha must be a numeric value")
    if alpha <= 0:
        raise ValueError("Alpha must be greater than 0")


def promethee_iii_ranking_validation(flows: pd.DataFrame, preferences: pd.DataFrame, alpha: NumericValue,
                                     decimal_place: NumericValue):
    """
    Validates input data for PrometheeIII calculation.

    :param flows: FlowsTable of both positive and negative outranking flows.
    :param preferences: PreferenceTable of alternatives over alternatives
    :param alpha: parameter used in calculating intervals
    :param decimal_place: with this you can choose the decimal_place of the output numbers

    :return: None
    """
    _check_flows(flows)
    _check_if_dataframe(preferences, "Preferences")
    _check_alpha(alpha)
    _check_decimal_place(decimal_place)
