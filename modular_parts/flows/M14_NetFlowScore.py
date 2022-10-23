"""
    This class computes Net Flow Score which bases on calculating scores associated with
    each alternative.
"""
import numpy as np
import pandas as pd
from core.aliases import PreferencesTable
from core.enums import ScoringFunction, ScoringFunctionDirection

__all__ = ['calculate_net_flows_score']


def _calculate_score(preferences: PreferencesTable,
                     function: ScoringFunction,
                     direction: ScoringFunctionDirection) -> np.array:
    """
    Calculates scores for passed preferences.

    :param preferences: 2D List of aggregated preferences between alternatives.
    :return: List of Net Flow Scores for passed preferences.
    """

    if function is ScoringFunction.MAX:
        function = np.nanmax
    elif function is ScoringFunction.MIN:
        function = np.nanmin
    elif function is ScoringFunction.SUM:
        function = np.nansum
    else:
        raise ValueError(f"Incorrect scoring function: {function}")

    if direction is ScoringFunctionDirection.IN_FAVOR:
        scores = function(preferences.values, axis=1)
    elif direction is ScoringFunctionDirection.AGAINST:
        scores = -function(preferences.values, axis=0)
    elif direction is ScoringFunctionDirection.DIFFERENCE:
        scores = function(preferences.values - preferences.values.T, axis=1)
    else:
        raise ValueError(f"Incorrect scoring function direction: {direction}")

    return scores


def _find_duplicates_values(array: np.ndarray) -> set:
    seen = set()
    duplicated_values = set()

    for x in array:
        if x in seen:
            duplicated_values.add(x)
        else:
            seen.add(x)

    return duplicated_values


def calculate_net_flows_score(preferences: PreferencesTable,
                              function: ScoringFunction,
                              direction: ScoringFunctionDirection,
                              avoid_same_scores: bool = False) -> pd.Series:
    """
    Calculates scores for all preferences.


    :param preferences: Preference table of aggregated preferences.
    :param function: Enum ScoringFunction - indicate which function should be used in calculating Net Flow Score.
    :param direction: Enum ScoringFunctionDirection - indicate which function direction should be used in
    :param avoid_same_scores: If True and calculate_scores returns some equal scores calculate once more scores for
                              alternatives which get the same score.
    :return: List of Net Flow Scores for all preferences.
    """
    np.fill_diagonal(preferences.values, np.NaN)

    if avoid_same_scores:
        scores = _calculate_score(preferences, function, direction)
        if len(scores) != len(set(scores)):
            duplicated_values = _find_duplicates_values(scores)
            for duplicated_value in duplicated_values:
                duplicated_score_indices = [i for i, score in enumerate(scores) if score == duplicated_value]
                sub_preferences = preferences.iloc[:, duplicated_score_indices].iloc[duplicated_score_indices, :]
                sub_scores = _calculate_score(sub_preferences, function, direction)
                for index, score in zip(duplicated_score_indices, sub_scores):
                    scores[index] = score
    else:
        scores = _calculate_score(preferences, function, direction)

    return pd.Series(scores, index=preferences.columns)
