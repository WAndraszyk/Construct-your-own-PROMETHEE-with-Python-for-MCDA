import pandas as pd
from enum import Enum

from typing import Tuple, Union

from core.enums import ScoringFunction, ScoringFunctionDirection

__all__ = ["net_flow_score_validation", "promethee_group_ranking_validation",
           "prometheeI_outranking_flows_validation", "prometheeII_outranking_flows_validation"]


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


def _check_if_dataframe(data_frame: pd.DataFrame, checked_object_name: str):
    if not isinstance(data_frame, pd.DataFrame):
        raise ValueError(f"{checked_object_name} should be passed as a DataFrame object")


def _check_avoid_same_scores(avoid_same_scores: bool):
    if not isinstance(avoid_same_scores, bool):
        raise ValueError("Avoid same scores parameter should have value True or False")


def net_flow_score_validation(alternative_preferences: pd.DataFrame, function: Enum,
                              direction: Enum, avoid_same_scores: bool):
    _check_if_dataframe(alternative_preferences, "Partial preferences")
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


# M9
def _check_tuple_len(tuple_to_check: Tuple, tuple_len: int, checked_object_name: str):
    if len(tuple_to_check) != tuple_len:
        raise ValueError(f"Tuple of {checked_object_name} should have {tuple_len} elements")


def _check_dtype(checked_object: Union[pd.DataFrame, pd.Series], checked_object_name: str):
    if not checked_object.dtypes not in [int, float]:
        raise ValueError(f"{checked_object_name} should be passed with int or float values")


def _check_columns_and_indices_in_tuple(preferences: Tuple[pd.DataFrame, pd.DataFrame]):
    if not preferences[0].index.equals(preferences[1].columns) or \
            not preferences[0].columns.equals(preferences[1].index):
        raise ValueError("Columns of one DataFrame should be equal to indices of the other")


def _check_if_alternatives_vs_alternatives(preferences: pd.DataFrame):
    if not preferences.index.equals(preferences.columns):
        raise ValueError("Indices and columns of preferences DataFrame should be the same")


def promethee_group_ranking_validation(dms_flows: pd.DataFrame, dms_weights: pd.Series):
    dms_from_flows = dms_flows.columns.unique()
    dms_from_weights = dms_weights.index

    _check_if_dataframe(dms_flows, "Partial preferences")
    _check_weights(dms_weights, len(dms_from_flows))
    _check_criteria(dms_from_flows, dms_from_weights)


def prometheeI_outranking_flows_validation(preferences: Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]):
    if isinstance(preferences, tuple):
        _check_tuple_len(preferences, 2, "Preferences")
        _check_if_dataframe(preferences[0], "Preferences")
        _check_if_dataframe(preferences[1], "Preferences")
        _check_dtype(preferences[0], "Preferences")
        _check_dtype(preferences[1], "Preferences")
        _check_columns_and_indices_in_tuple(preferences)
    else:
        _check_if_dataframe(preferences, "Preferences")
        _check_dtype(preferences, "Preferences")
        _check_if_alternatives_vs_alternatives(preferences)


def prometheeII_outranking_flows_validation(preferences: Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]):
    if isinstance(preferences, tuple):
        _check_tuple_len(preferences, 2, "Preferences")
        _check_if_dataframe(preferences[0], "Preferences")
        _check_if_dataframe(preferences[1], "Preferences")
        _check_dtype(preferences[0], "Preferences")
        _check_dtype(preferences[1], "Preferences")
        _check_columns_and_indices_in_tuple(preferences)
    else:
        raise ValueError("Preferences should be passed as a tuple of DataFrames")
