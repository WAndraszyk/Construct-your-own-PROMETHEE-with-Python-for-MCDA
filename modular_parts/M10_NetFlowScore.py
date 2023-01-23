"""
    .. image:: prometheePUT_figures/M10.png

    This class computes Net Flow Score which bases on calculating scores
    associated with each alternative.

    Implementation and naming of conventions are taken from
    :cite:p:`KadzinskiMichalski2016` and :cite:p:`BouyssouPerny1992`.
"""
import math

import numpy as np
import pandas as pd

from core.enums import ScoringFunction, ScoringFunctionDirection
from core.input_validation.flow import net_flow_score_validation

__all__ = ["calculate_net_flows_score"]


def _calculate_score(
    preferences: pd.DataFrame,
    function: ScoringFunction,
    direction: ScoringFunctionDirection,
) -> np.ndarray:
    """
    This function calculates scores for passed preferences.

    :param preferences: pd.DataFrame with alternatives names as index
        and columns
    :param function: ScoringFunction that determines scoring function
        used in calculation
    :param direction: ScoringFunctionDirection that determines scoring
        function direction used in calculation

    :return: np.ndarray with net flow scores for passed preferences
    """

    # Scoring function selection
    if function is ScoringFunction.MAX:
        function_callable = np.nanmax
    elif function is ScoringFunction.MIN:
        function_callable = np.nanmin
    else:
        function_callable = np.nansum

    # Scoring function direction selection
    if direction is ScoringFunctionDirection.IN_FAVOR:
        scores = function_callable(preferences.values, axis=1)
    elif direction is ScoringFunctionDirection.AGAINST:
        scores = -function_callable(preferences.values, axis=0)
    else:
        scores = function_callable(preferences.values - preferences.values.T, axis=1)
    return scores


def _find_duplicates_values(array: np.ndarray) -> set:
    """
    This function finds duplicated values.

    :param array: np.ndarray with net flow scores for passed preferences

    :return: set with duplicated values
    """
    seen = set()
    duplicated_values = set()

    for x in array:
        if x in seen:
            duplicated_values.add(x)
        else:
            seen.add(x)

    return duplicated_values


def calculate_net_flows_score(
    preferences: pd.DataFrame,
    function: ScoringFunction,
    direction: ScoringFunctionDirection,
    avoid_same_scores: bool = False,
) -> pd.Series:
    """
    This function calculates net flow scores for all preferences.

    :param preferences: pd.DataFrame with alternatives names as index
        and columns
    :param function: ScoringFunction that determines scoring function
        used in calculation
    :param direction: ScoringFunctionDirection that determines scoring
        function direction used in calculation
    :param avoid_same_scores: bool, that determines if equal values are
        allowed in result

    :return: pd.Series with net flow scores for all preferences
    """
    net_flow_score_validation(preferences, function, direction, avoid_same_scores)
    np.fill_diagonal(preferences.values, np.NaN)

    if avoid_same_scores:
        scores = _calculate_score(preferences, function, direction)

        # Repeat calculations for duplicate values
        if len(scores) != len(set(scores)):
            duplicated_values = _find_duplicates_values(scores)
            for duplicated_value in duplicated_values:
                duplicated_score_indices = [
                    i
                    for i, score in enumerate(scores)
                    if math.isclose(score, duplicated_value)
                ]
                sub_preferences = preferences.iloc[:, duplicated_score_indices].iloc[
                    duplicated_score_indices, :
                ]
                sub_scores = _calculate_score(sub_preferences, function, direction)
                for index, score in zip(duplicated_score_indices, sub_scores):
                    scores[index] = score
    else:
        scores = _calculate_score(preferences, function, direction)

    return pd.Series(scores, index=preferences.columns)
