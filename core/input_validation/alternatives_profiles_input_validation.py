import pandas as pd

__all__ = ["alternatives_profiles_validation", "_check_weights", "_check_partial_preferences"]


# M10
def _check_weights(weights: pd.Series, criteria_num: int):
    if not isinstance(weights, pd.Series):
        raise ValueError("Criteria weights should be passed as a Series object")

    if len(weights) != criteria_num:
        raise ValueError("Number of weights should be equals to number of criteria")

    for weight in weights:
        if not isinstance(weight, (int, float)):
            raise ValueError("Weights should be a numeric values")

    if (weights <= 0).any():
        raise ValueError("Weights should be positive")


def _check_partial_preferences(partial_preferences: pd.DataFrame):
    if not isinstance(partial_preferences, pd.DataFrame):
        raise ValueError("Partial preferences should be passed as a DataFrame object")


def _check_criteria(criteria_from_series: pd.Index, criteria_from_df: pd.Index):
    if not criteria_from_series.equals(criteria_from_df):
        raise ValueError("Criteria defined in criteria weights should be the same as in partial preferences")


def alternatives_profiles_validation(criteria_weights: pd.Series, partial_preferences: pd.DataFrame):
    criteria_from_df = partial_preferences.index.get_level_values(0).unique()
    criteria_from_series = criteria_weights.index

    _check_weights(criteria_weights, len(criteria_from_df))
    _check_partial_preferences(partial_preferences)
    _check_criteria(criteria_from_series, criteria_from_df)
