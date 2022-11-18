import pandas as pd
from enum import Enum
from core.enums import ScoringFunction, ScoringFunctionDirection

__all__ = ["net_flow_score_validation", "promethee_group_ranking_validation"]


# M14
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


def _check_if_dataframe(data_frame: pd.DataFrame):
    if not isinstance(data_frame, pd.DataFrame):
        raise ValueError("Partial preferences should be passed as a DataFrame object")


def _check_avoid_same_scores(avoid_same_scores: bool):
    if not isinstance(avoid_same_scores, bool):
        raise ValueError("Avoid same scores parameter should have value True or False")


def net_flow_score_validation(alternative_preferences: pd.DataFrame, function: Enum,
                              direction: Enum, avoid_same_scores: bool):
    _check_if_dataframe(alternative_preferences)
    _check_enums(function, direction)
    _check_avoid_same_scores(avoid_same_scores)


# M16
def _check_weights(dms_weights: pd.Series, dms_num: int):
    if not isinstance(dms_weights, pd.Series):
        raise ValueError("DMs weights should be passed as a Series object")

    if len(dms_weights) != dms_num:
        raise ValueError("Number of weights should be equals to number of DMs")

    for weight in dms_weights:
        if not isinstance(weight, (int, float)):
            raise ValueError("Weights should be a numeric values")


def _check_criteria(dms_from_flows: pd.Index, dms_from_weights: pd.Index):
    if not dms_from_flows.equals(dms_from_weights):
        raise ValueError("Criteria defined in DMs weights should be the same as in DMs flows DataFrame")


def promethee_group_ranking_validation(dms_flows: pd.DataFrame, dms_weights: pd.Series):
    dms_from_flows = dms_flows.columns.unique()
    dms_from_weights = dms_weights.index

    _check_if_dataframe(dms_flows)
    _check_weights(dms_weights, len(dms_from_flows))
    _check_criteria(dms_from_flows, dms_from_weights)
