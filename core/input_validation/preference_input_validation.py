from typing import List, Union, Tuple

import pandas as pd
from core.aliases import PerformanceTable, NumericValue
from core.enums import Direction

__all__ = ["promethee_preference_validation", "reinforced_preference_validation", "discordance_validation",
           "_check_decimal_place", "_check_if_dataframe"]


def _check_performances(performance_table: pd.DataFrame, criteria: pd.Index):
    if not isinstance(performance_table, pd.DataFrame):
        raise TypeError("Performances on criteria should be passed as a DataFrame object")
    _compare_criteria(performance_table.columns, criteria)


def _check_preference_thresholds(preference_thresholds: pd.Series, criteria: pd.Index):
    if not isinstance(preference_thresholds, pd.Series):
        raise TypeError("Preference thresholds should be passed as a DataSeries object")
    _compare_criteria(preference_thresholds.index, criteria)
    if len(preference_thresholds) != len(criteria):
        raise ValueError("Number of preference thresholds should be equal to number of criteria")
    for i in preference_thresholds:
        if i is not None:
            if not isinstance(i, (int, float)):
                raise TypeError("Preference thresholds should be numerical values")
            if i < 0:
                raise ValueError("Preference threshold can not be lower than 0")


def _check_indifference_thresholds(indifference_thresholds: pd.Series, criteria: pd.Index):
    if not isinstance(indifference_thresholds, pd.Series):
        raise TypeError("Indifference thresholds should be passed as a DataSeries object")
    _compare_criteria(indifference_thresholds.index, criteria)
    if len(indifference_thresholds) != len(criteria):
        raise ValueError("Number of indifference thresholds should be equal to number of criteria")
    for i in indifference_thresholds:
        if i is not None:
            if not isinstance(i, (int, float)):
                raise TypeError("Indifference thresholds should be numerical values")
            if i < 0:
                raise ValueError("Indifference threshold can not be lower than 0")


def _check_standard_deviations(standard_deviations: pd.Series, criteria: pd.Index):
    if not isinstance(standard_deviations, pd.Series):
        raise TypeError("Standard deviations should be passed as a DataSeries object")
    _compare_criteria(standard_deviations.index, criteria)
    if len(standard_deviations) != len(criteria):
        raise ValueError("Number of standard deviations should be equal to number of criteria")
    for i in standard_deviations:
        if i is not None:
            if not isinstance(i, (int, float)):
                raise TypeError("Standard deviations should be numeric values")
            if i < 0:
                raise ValueError("Standard deviation can not be lower than 0")


def _check_generalized_criteria(generalized_criteria: pd.Series, criteria: pd.Index):
    if not isinstance(generalized_criteria, pd.Series):
        raise TypeError("Generalized criteria should be passed as a DataSeries object")
    _compare_criteria(generalized_criteria.index, criteria)
    if len(generalized_criteria) != len(criteria):
        raise ValueError("Number of generalized criteria should be equal to number of criteria")


def _check_directions(directions: pd.Series, criteria: pd.Index):
    if not isinstance(directions, pd.Series):
        raise TypeError("Directions should be passed as a DataSeries object")
    _compare_criteria(directions.index, criteria)
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


def _check_weights(weights: pd.Series):
    if not isinstance(weights, pd.Series):
        raise ValueError("Criteria weights should be passed as a Series object")
    for weight in weights:
        if not isinstance(weight, (int, float)):
            raise ValueError("Weights should be numeric values")


def _check_decimal_place(decimal_place: int):
    if not isinstance(decimal_place, int):
        raise TypeError("Decimal place must be integer")
    if decimal_place < 0:
        raise ValueError("Decimal place must be positive")


def _compare_criteria(criteria_from_series: pd.Index, criteria_from_df: pd.Index):
    if not criteria_from_series.equals(criteria_from_df):
        raise ValueError("Criteria do not match in all inputs")


def promethee_preference_validation(alternatives_performances: PerformanceTable, preference_thresholds: pd.Series,
                                    indifference_thresholds: pd.Series, standard_deviations: pd.Series,
                                    generalized_criteria: pd.Series, directions: pd.Series, weights: pd.Series,
                                    profiles_performance: PerformanceTable,
                                    decimal_place: NumericValue):
    """
    Validates input data for Promethee Preference calculation.
    :param alternatives_performances: Dataframe of alternatives' value at every criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param standard_deviations: standard deviation for each criterion
    :param generalized_criteria: list of preference functions
    :param directions: directions of preference of criteria
    :param weights: criteria with weights
    :param profiles_performance: Dataframe of profiles performance (value) at every criterion
    :param decimal_place: with this you can choose the decimal_place of the output numbers
    :return: None
    """
    _check_weights(weights)
    criteria = weights.index
    _check_performances(alternatives_performances, criteria)
    _check_preference_thresholds(preference_thresholds, criteria)
    _check_indifference_thresholds(indifference_thresholds, criteria)
    _check_standard_deviations(standard_deviations, criteria)
    _check_generalized_criteria(generalized_criteria, criteria)
    _check_directions(directions, criteria)
    _check_decimal_place(decimal_place)
    if profiles_performance is not None:
        _check_performances(profiles_performance, criteria)


def _check_reinforced_preference_thresholds(reinforced_preference_thresholds: pd.Series, criteria: pd.Index):
    if not isinstance(reinforced_preference_thresholds, pd.Series):
        raise TypeError("Reinforced preference thresholds should be passed as a DataSeries object")
    _compare_criteria(reinforced_preference_thresholds.index, criteria)
    if len(reinforced_preference_thresholds) != len(criteria):
        raise ValueError("Number of reinforced preference thresholds should be equal to number of criteria")
    for i in reinforced_preference_thresholds:
        if i is not None:
            if not isinstance(i, (int, float)):
                raise TypeError("Reinforced preference thresholds should be numerical values")
            if i < 0:
                raise ValueError("Reinforced preference threshold can not be lower than 0")


def _check_reinforcement_factors(reinforcement_factors: pd.Series, criteria: pd.Index):
    if not isinstance(reinforcement_factors, pd.Series):
        raise TypeError("Reinforcement factors should be passed as a DataSeries object")
    _compare_criteria(reinforcement_factors.index, criteria)
    if len(reinforcement_factors) != len(criteria):
        raise ValueError("Number of reinforcement factors should be equal to number of criteria")
    for i in reinforcement_factors:
        if i is not None:
            if not isinstance(i, (int, float)):
                raise TypeError("Reinforcement factors should be numerical values")
            if i <= 1:
                raise ValueError("Reinforcement factors need to be >1")


def reinforced_preference_validation(alternatives_performances: PerformanceTable, preference_thresholds: pd.Series,
                                     indifference_thresholds: pd.Series, generalized_criteria: pd.Series,
                                     directions: pd.Series, reinforced_preference_thresholds: pd.Series,
                                     reinforcement_factors: pd.Series, weights: pd.Series,
                                     profiles_performance: PerformanceTable,
                                     decimal_place: NumericValue):
    """
    Validates input data for Reinforced Preference calculation.
    :param alternatives_performances: Dataframe of alternatives' value at every criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param generalized_criteria: list of preference functions
    :param directions: directions of preference of criteria
    :param reinforced_preference_thresholds: list of reinforced preference threshold for each criterion
    :param reinforcement_factors: list of reinforcement factor for each criterion
    :param weights: criteria with weights
    :param profiles_performance: Dataframe of profiles performance (value) at every criterion
    :param decimal_place: with this you can choose the decimal_place of the output numbers
    :return: None
    """
    _check_weights(weights)
    criteria = weights.index
    _check_performances(alternatives_performances, criteria)
    _check_preference_thresholds(preference_thresholds, criteria)
    _check_indifference_thresholds(indifference_thresholds, criteria)
    _check_generalized_criteria(generalized_criteria, criteria)
    _check_directions(directions, criteria)
    _check_reinforced_preference_thresholds(reinforced_preference_thresholds, criteria)
    _check_reinforcement_factors(reinforcement_factors, criteria)
    _check_decimal_place(decimal_place)
    if profiles_performance is not None:
        _check_performances(profiles_performance, criteria)


def _check_criteria(criteria: List[str]):
    if not isinstance(criteria, list):
        raise TypeError("Criteria should be passed as a list object")
    for k in criteria:
        if not isinstance(k, str):
            raise TypeError("Criterion should be a string")


def _check_partial_preferences(partial_preferences: pd.DataFrame):
    if not isinstance(partial_preferences, tuple):
        if not isinstance(partial_preferences, pd.DataFrame):
            raise TypeError("Partial preferences should be passed as a DataFrame object")
    else:
        if len(partial_preferences) != 2:
            raise TypeError("Partial preferences with profiles should be passed as tuple of two DataFrames")
        if not isinstance(partial_preferences[0], pd.DataFrame) or not isinstance(partial_preferences[1], pd.DataFrame):
            raise TypeError("Partial preferences with profiles should be passed as tuple of two DataFrames")


def _check_tau(tau: NumericValue, criteria: List[str]):
    if not isinstance(tau, (int, float)):
        raise TypeError("Tau should be a numeric value")
    if tau < 1 or tau > len(criteria):
        raise ValueError("Tau needs to be a number from 1 to k, where k is the number of criteria.")


def _check_categories_profiles(categories_profiles: bool):
    if not isinstance(categories_profiles, bool):
        raise TypeError("Categories profiles should be a boolean value")


def _check_if_dataframe(data_frame: pd.DataFrame, checked_object_name: str):
    if not isinstance(data_frame, pd.DataFrame):
        raise ValueError(f"{checked_object_name} should be passed as a DataFrame object")


def _check_preferences(preferences: Union[pd.DataFrame, Tuple[pd.DataFrame]]):
    if not isinstance(preferences, tuple):
        if not isinstance(preferences, pd.DataFrame):
            raise TypeError("Preferences should be passed as a DataFrame object")
    else:
        if len(preferences) != 2:
            raise TypeError("Preferences with profiles should be passed as tuple of two DataFrames")
        if not isinstance(preferences[0], pd.DataFrame) or not isinstance(preferences[1], pd.DataFrame):
            raise TypeError("Preferences with profiles should be passed as tuple of two DataFrames")


def discordance_validation(criteria: List[str], partial_preferences: Union[pd.DataFrame, Tuple[pd.DataFrame]],
                           tau: NumericValue, decimal_place: NumericValue,
                           preferences: Union[pd.DataFrame, Tuple[pd.DataFrame]], categories_profiles: bool):
    """
    Validates input data for Discordance calculation.

    :param tau: technical parameter, τ ∈ [1, k], smaller τ → weaker discordance
    :param decimal_place: with this you can choose the decimal_place of the output numbers
    :param preferences: if not empty function returns already calculated preference instead of just discordance
    :param criteria: list of criteria names
    :param partial_preferences: partial preference of every alternative over other alternatives or profiles
    :param categories_profiles: were the preferences calculated for profiles

    :return: None
    """
    _check_criteria(criteria)
    _check_partial_preferences(partial_preferences)
    _check_tau(tau, criteria)
    _check_decimal_place(decimal_place)
    if preferences is not None:
        _check_preferences(preferences)
    _check_categories_profiles(categories_profiles)
