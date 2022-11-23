import pandas as pd
from core.aliases import PerformanceTable, NumericValue
from core.enums import PreferenceFunction, Direction

__all__ = ["promethee_preference_validation"]


def _check_performances(performance_table: pd.DataFrame, criteria: pd.Index):
    _check_criteria(performance_table.columns, criteria)
    if not isinstance(performance_table, pd.DataFrame):
        raise TypeError("Performances on criteria should be passed as a DataFrame object")


def _check_preference_thresholds(preference_thresholds: pd.Series, criteria: pd.Index):
    _check_criteria(preference_thresholds.index, criteria)
    if not isinstance(preference_thresholds, pd.Series):
        raise TypeError("Preference thresholds should be passed as a DataSeries object")
    if len(preference_thresholds) != len(criteria):
        raise ValueError("Number of preference thresholds should be equal to number of criteria")
    values = preference_thresholds.values
    for i in values:
        if i is not None:
            if not isinstance(i, (int, float)):
                raise TypeError("Preference thresholds should be numerical values")
            if i < 0:
                raise ValueError("Preference threshold can not be lower than 0")


def _check_indifference_thresholds(indifference_thresholds: pd.Series, criteria: pd.Index):
    _check_criteria(indifference_thresholds.index, criteria)
    if not isinstance(indifference_thresholds, pd.Series):
        raise TypeError("Indifference thresholds should be passed as a DataSeries object")
    if len(indifference_thresholds) != len(criteria):
        raise ValueError("Number of indifference thresholds should be equal to number of criteria")
    values = indifference_thresholds.values
    for i in values:
        if i is not None:
            if not isinstance(i, (int, float)):
                raise TypeError("Indifference thresholds should be numerical values")
            if i < 0:
                raise ValueError("Indifference threshold can not be lower than 0")


def _check_standard_deviations(standard_deviations: pd.Series, criteria: pd.Index):
    _check_criteria(standard_deviations.index, criteria)
    if not isinstance(standard_deviations, pd.Series):
        raise TypeError("Standard deviations should be passed as a DataSeries object")
    if len(standard_deviations) != len(criteria):
        raise ValueError("Number of standard deviations should be equal to number of criteria")
    values = standard_deviations.values
    for i in values:
        if i is not None:
            if not isinstance(i, (int, float)):
                raise TypeError("Standard deviations should be numeric values")
            if i < 0:
                raise ValueError("Standard deviation can not be lower than 0")


def _check_generalized_criteria(generalized_criteria: pd.Series, criteria: pd.Index):
    _check_criteria(generalized_criteria.index, criteria)
    if not isinstance(generalized_criteria, pd.Series):
        raise TypeError("Generalized criteria should be passed as a DataSeries object")
    if len(generalized_criteria) != len(criteria):
        raise ValueError("Number of generalized criteria should be equal to number of criteria")


def _check_directions(directions: pd.Series, criteria: pd.Index):
    _check_criteria(directions.index, criteria)
    if not isinstance(directions, pd.Series):
        raise TypeError("Directions should be passed as a DataSeries object")
    if len(directions) != len(criteria):
        raise ValueError("Number of directions should be equal to number of criteria")
    for k in criteria:
        direction = directions[k]
        if direction is Direction.MIN:
            continue
        if direction is Direction.MAX:
            continue
        else:
            raise ValueError(f"Incorrect direction: {direction}")


def _check_weights(weights: pd.Series, criteria: pd.Index):
    _check_criteria(weights.index, criteria)
    if not isinstance(weights, pd.Series):
        raise ValueError("Criteria weights should be passed as a Series object")

    if len(weights) != len(criteria):
        raise ValueError("Number of weights should be equal to number of criteria")

    for weight in weights:
        if not isinstance(weight, (int, float)):
            raise ValueError("Weights should be numeric values")


def _check_decimal_place(decimal_place: int):
    if not isinstance(decimal_place, int):
        raise TypeError("Decimal place must be integer")
    if decimal_place < 0:
        raise ValueError("Decimal place must be positive")


def _check_criteria(criteria_from_series: pd.Index, criteria_from_df: pd.Index):
    if not criteria_from_series.equals(criteria_from_df):
        raise ValueError("Criteria do not match in all inputs")


def promethee_preference_validation(alternatives_performances: PerformanceTable, preference_thresholds: pd.Series,
                                    indifference_thresholds: pd.Series, standard_deviations: pd.Series,
                                    generalized_criteria: pd.Series, directions: pd.Series, weights: pd.Series,
                                    profiles_performance: PerformanceTable,
                                    decimal_place: NumericValue, criteria: pd.Index):
    _check_performances(alternatives_performances, criteria)
    _check_preference_thresholds(preference_thresholds, criteria)
    _check_indifference_thresholds(indifference_thresholds, criteria)
    _check_standard_deviations(standard_deviations, criteria)
    _check_generalized_criteria(generalized_criteria, criteria)
    _check_directions(directions, criteria)
    _check_weights(weights, criteria)
    _check_decimal_place(decimal_place)
    if profiles_performance is not None:
        _check_performances(profiles_performance, criteria)
