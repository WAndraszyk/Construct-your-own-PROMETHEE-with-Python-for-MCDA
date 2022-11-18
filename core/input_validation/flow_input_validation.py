import pandas as pd
from enum import Enum
from core.enums import ScoringFunction, ScoringFunctionDirection

__all__ = ["net_flow_score_validation"]


def _check_enums(function: Enum, direction: Enum):
    if function is ScoringFunction.MAX:
        pass
    elif function is ScoringFunction.MIN:
        pass
    elif function is ScoringFunction.SUM:
        pass
    else:
        raise ValueError(f"Incorrect scoring function: {function}")

    if direction is ScoringFunctionDirection.IN_FAVOR:
        pass
    elif direction is ScoringFunctionDirection.AGAINST:
        pass
    elif direction is ScoringFunctionDirection.DIFFERENCE:
        pass
    else:
        raise ValueError(f"Incorrect scoring function direction: {direction}")


def _check_alternative_preferences(partial_preferences: pd.DataFrame):
    if not isinstance(partial_preferences, pd.DataFrame):
        raise ValueError("Partial preferences should be passed as a DataFrame object")


def _check_avoid_same_scores(avoid_same_scores: bool):
    if not isinstance(avoid_same_scores, bool):
        raise ValueError("Avoid same scores parameter should have value True or False")


def net_flow_score_validation(alternative_preferences: pd.DataFrame, function: Enum,
                              direction: Enum, avoid_same_scores: bool):
    _check_alternative_preferences(alternative_preferences)
    _check_enums(function, direction)
    _check_avoid_same_scores(avoid_same_scores)
