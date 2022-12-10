from typing import List, Union, Tuple

import pandas as pd
from core.aliases import NumericValue
from core.enums import Direction, InteractionType

__all__ = ["promethee_preference_validation",
           "reinforced_preference_validation", "discordance_validation",
           "_check_decimal_place", "_check_if_dataframe",
           "promethee_interaction_preference_validation", "veto_validation"]


def _check_performances(performance_table: pd.DataFrame, criteria: pd.Index):
    if not isinstance(performance_table, pd.DataFrame):
        raise TypeError("Performances on criteria should be passed "
                        "as a DataFrame object")
    _compare_criteria(performance_table.columns, criteria)


def _check_preference_thresholds(preference_thresholds: pd.Series,
                                 criteria: pd.Index):
    if not isinstance(preference_thresholds, pd.Series):
        raise TypeError("Preference thresholds should be passed as "
                        "a DataSeries object")
    _compare_criteria(preference_thresholds.index, criteria)
    if len(preference_thresholds) != len(criteria):
        raise ValueError("Number of preference thresholds should be "
                         "equal to number of criteria")
    for i in preference_thresholds:
        if i is not None:
            if not isinstance(i, (int, float)):
                raise TypeError("Preference thresholds should be "
                                "numerical values")
            if i < 0:
                raise ValueError("Preference threshold can not be "
                                 "lower than 0")


def _check_indifference_thresholds(indifference_thresholds: pd.Series,
                                   criteria: pd.Index):
    if not isinstance(indifference_thresholds, pd.Series):
        raise TypeError("Indifference thresholds should be passed as a "
                        "DataSeries object")
    _compare_criteria(indifference_thresholds.index, criteria)
    if len(indifference_thresholds) != len(criteria):
        raise ValueError("Number of indifference thresholds should be"
                         " equal to number of criteria")
    for i in indifference_thresholds:
        if i is not None:
            if not isinstance(i, (int, float)):
                raise TypeError("Indifference thresholds should be"
                                " numerical values")
            if i < 0:
                raise ValueError("Indifference threshold can not be "
                                 "lower than 0")


def _check_standard_deviations(standard_deviations: pd.Series,
                               criteria: pd.Index):
    if not isinstance(standard_deviations, pd.Series):
        raise TypeError("Standard deviations should be passed as a "
                        "DataSeries object")
    _compare_criteria(standard_deviations.index, criteria)
    if len(standard_deviations) != len(criteria):
        raise ValueError("Number of standard deviations should be equal "
                         "to number of criteria")
    for i in standard_deviations:
        if i is not None:
            if not isinstance(i, (int, float)):
                raise TypeError("Standard deviations should be numeric "
                                "values")
            if i < 0:
                raise ValueError("Standard deviation can not be lower than 0")


def _check_veto_thresholds(veto_thresholds: pd.Series, criteria: pd.Index):
    if not isinstance(veto_thresholds, pd.Series):
        raise TypeError("Veto thresholds should be passed as a "
                        "DataSeries object")
    _compare_criteria(veto_thresholds.index, criteria)
    if len(veto_thresholds) != len(criteria):
        raise ValueError("Number of veto thresholds should be equal to "
                         "number of criteria")
    for i in veto_thresholds:
        if i is not None:
            if not isinstance(i, (int, float)):
                raise TypeError("Veto thresholds should be numeric values")
            if i < 0:
                raise ValueError("Veto thresholds can not be lower than 0")


def _check_generalized_criteria(generalized_criteria: pd.Series,
                                criteria: pd.Index):
    if not isinstance(generalized_criteria, pd.Series):
        raise TypeError("Generalized criteria should be passed as a "
                        "DataSeries object")
    _compare_criteria(generalized_criteria.index, criteria)
    if len(generalized_criteria) != len(criteria):
        raise ValueError("Number of generalized criteria should be equal "
                         "to number of criteria")


def _check_directions(directions: pd.Series, criteria: pd.Index):
    if not isinstance(directions, pd.Series):
        raise TypeError("Directions should be passed as a DataSeries object")
    _compare_criteria(directions.index, criteria)
    if len(directions) != len(criteria):
        raise ValueError("Number of directions should be equal to"
                         " number of criteria")
    for k in criteria:
        direction = directions[k]
        if direction is Direction.MIN:
            continue
        elif direction is Direction.MAX:
            continue
        else:
            raise ValueError(f"Incorrect direction: {direction}")


def _check_weights(weights: pd.Series):
    if not isinstance(weights, pd.Series):
        raise ValueError("Criteria weights should be passed as a "
                         "Series object")
    for weight in weights:
        if not isinstance(weight, (int, float)):
            raise ValueError("Weights should be numeric values")


def _check_decimal_place(decimal_place: int):
    if not isinstance(decimal_place, int):
        raise TypeError("Decimal place must be integer")
    if decimal_place < 0:
        raise ValueError("Decimal place must be positive")


def _compare_criteria(criteria_from_series: pd.Index,
                      criteria_from_df: pd.Index):
    if not criteria_from_series.equals(criteria_from_df):
        raise ValueError("Criteria do not match in all inputs")


def promethee_preference_validation(alternatives_performances: pd.DataFrame,
                                    preference_thresholds: pd.Series,
                                    indifference_thresholds: pd.Series,
                                    standard_deviations: pd.Series,
                                    generalized_criteria: pd.Series,
                                    directions: pd.Series, weights: pd.Series,
                                    profiles_performance: pd.DataFrame,
                                    decimal_place: NumericValue):
    """
    Validates input data for Promethee Preference calculation.
    :param alternatives_performances: Dataframe of alternatives' value at
    every criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param standard_deviations: standard deviation for each criterion
    :param generalized_criteria: list of preference functions
    :param directions: directions of preference of criteria
    :param weights: criteria with weights
    :param profiles_performance: Dataframe of profiles performance (value) at
    every criterion
    :param decimal_place: with this you can choose the decimal_place of the
    output numbers
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


def promethee_interaction_preference_validation(
        alternatives_performances: pd.DataFrame,
        preference_thresholds: pd.Series,
        indifference_thresholds: pd.Series,
        standard_deviations: pd.Series,
        generalized_criteria: pd.Series,
        directions: pd.Series,
        weights: pd.Series,
        profiles_performance: pd.DataFrame,
        interactions: pd.DataFrame,
        minimum_interaction_effect: bool,
        decimal_place: NumericValue):
    """
    Validates input data for Promethee Preference calculation.
    :param alternatives_performances: Dataframe of alternatives' value at
     every criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param standard_deviations: standard deviation for each criterion
    :param generalized_criteria: list of preference functions
    :param directions: directions of preference of criteria
    :param weights: criteria with weights
    :param profiles_performance: Dataframe of profiles performance (value)
    at every criterion
    :param decimal_place: with this you can choose the decimal_place of the
    output numbers
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
    _check_interactions(interactions, criteria)
    _check_minimum_interaction_effect(minimum_interaction_effect)
    if profiles_performance is not None:
        _check_performances(profiles_performance, criteria)


def _check_interactions(interactions: pd.DataFrame, criteria: pd.Series):
    if not isinstance(interactions, pd.DataFrame):
        raise TypeError(
            "Performances on criteria should be passed as a DataFrame object")
    _check_interaction_columns(interactions.columns)
    _check_interactions_criteria(interactions['criterion_1'], criteria)
    _check_interactions_criteria(interactions['criterion_2'], criteria)
    _check_interactions_types(interactions['type'])
    _check_interaction_coefficient(interactions[['type', 'coefficient']])


def _check_interaction_columns(column_names: pd.Index):
    if list(column_names.values) != ['criterion_1', 'criterion_2', 'type',
                                     'coefficient']:
        raise TypeError(
            "Interactions columns should be names as 'criterion_1', "
            "'criterion_2', 'type', 'coefficient'")


def _check_interactions_criteria(column: pd.Series, criteria: pd.Series):
    for value in column.values:
        if value not in list(criteria.values):
            raise TypeError("Criteria names in interactions are not valid!")


def _check_interactions_types(interactions: pd.DataFrame):
    for type in list(interactions.values):
        if type is InteractionType.STN:
            continue
        elif type is InteractionType.WKN:
            continue
        elif type is InteractionType.ANT:
            continue
        else:
            raise ValueError(f"Incorrect interaction type: {type}")


def _check_interaction_coefficient(interactions: pd.DataFrame):
    for _, row in interactions.iterrows():
        if row['type'] is InteractionType.WKN:
            if row['coefficient'] > 0:
                raise TypeError("Mutual weakening coefficient must be < 0!")
        elif row['coefficient'] < 0:
            raise TypeError(
                "Mutual antagonistic and strengthening "
                "coefficients must be > 0!")


def _check_reinforced_preference_thresholds(
        reinforced_preference_thresholds: pd.Series, criteria: pd.Index):
    if not isinstance(reinforced_preference_thresholds, pd.Series):
        raise TypeError(
            "Reinforced preference thresholds should"
            " be passed as a DataSeries object")
    _compare_criteria(reinforced_preference_thresholds.index, criteria)
    if len(reinforced_preference_thresholds) != len(criteria):
        raise ValueError(
            "Number of reinforced preference thresholds"
            " should be equal to number of criteria")
    for i in reinforced_preference_thresholds:
        if i is not None:
            if not isinstance(i, (int, float)):
                raise TypeError(
                    "Reinforced preference thresholds "
                    "should be numerical values")
            if i < 0:
                raise ValueError(
                    "Reinforced preference threshold can not be lower than 0")


def _check_reinforcement_factors(reinforcement_factors: pd.Series,
                                 criteria: pd.Index):
    if not isinstance(reinforcement_factors, pd.Series):
        raise TypeError(
            "Reinforcement factors should be passed as a DataSeries object")
    _compare_criteria(reinforcement_factors.index, criteria)
    if len(reinforcement_factors) != len(criteria):
        raise ValueError(
            "Number of reinforcement factors should be equal "
            "to number of criteria")
    for i in reinforcement_factors:
        if i is not None:
            if not isinstance(i, (int, float)):
                raise TypeError(
                    "Reinforcement factors should be numerical values")
            if i <= 1:
                raise ValueError("Reinforcement factors need to be >1")


def reinforced_preference_validation(
        alternatives_performances: pd.DataFrame,
        preference_thresholds: pd.Series,
        indifference_thresholds: pd.Series,
        generalized_criteria: pd.Series,
        directions: pd.Series,
        reinforced_preference_thresholds: pd.Series,
        reinforcement_factors: pd.Series,
        weights: pd.Series,
        profiles_performance: pd.DataFrame,
        decimal_place: NumericValue):
    """
    Validates input data for Reinforced Preference calculation.
    :param alternatives_performances: Dataframe of alternatives' value at
    every criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param generalized_criteria: list of preference functions
    :param directions: directions of preference of criteria
    :param reinforced_preference_thresholds: list of reinforced preference
    threshold for each criterion
    :param reinforcement_factors: list of reinforcement factor for each
    criterion
    :param weights: criteria with weights
    :param profiles_performance: Dataframe of profiles performance (value)
    at every criterion
    :param decimal_place: with this you can choose the decimal_place of the
     output numbers
    :return: None
    """
    _check_weights(weights)
    criteria = weights.index
    _check_performances(alternatives_performances, criteria)
    _check_preference_thresholds(preference_thresholds, criteria)
    _check_indifference_thresholds(indifference_thresholds, criteria)
    _check_generalized_criteria(generalized_criteria, criteria)
    _check_directions(directions, criteria)
    _check_reinforced_preference_thresholds(reinforced_preference_thresholds,
                                            criteria)
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
            raise TypeError(
                "Partial preferences should be passed as a DataFrame object")
    else:
        if len(partial_preferences) != 2:
            raise TypeError(
                "Partial preferences with profiles should be"
                " passed as tuple of two DataFrames")
        if not isinstance(partial_preferences[0],
                          pd.DataFrame) or not isinstance(
            partial_preferences[1], pd.DataFrame):
            raise TypeError(
                "Partial preferences with profiles should be "
                "passed as tuple of two DataFrames")


def _check_tau(tau: NumericValue, criteria: List[str]):
    if not isinstance(tau, (int, float)):
        raise TypeError("Tau should be a numeric value")
    if tau < 1 or tau > len(criteria):
        raise ValueError(
            "Tau needs to be a number from 1 to k, where k "
            "is the number of criteria.")


def _check_categories_profiles(categories_profiles: bool):
    if not isinstance(categories_profiles, bool):
        raise TypeError("Categories profiles should be a boolean value")


def _check_if_dataframe(data_frame: pd.DataFrame, checked_object_name: str):
    if not isinstance(data_frame, pd.DataFrame):
        raise ValueError(
            f"{checked_object_name} should be passed as a DataFrame object")


def _check_preferences(preferences: Union[pd.DataFrame, Tuple[pd.DataFrame]]):
    if not isinstance(preferences, tuple):
        if not isinstance(preferences, pd.DataFrame):
            raise TypeError(
                "Preferences should be passed as a DataFrame object")
    else:
        if len(preferences) != 2:
            raise TypeError(
                "Preferences with profiles should be passed as "
                "tuple of two DataFrames")
        if not isinstance(preferences[0], pd.DataFrame) or not isinstance(
                preferences[1], pd.DataFrame):
            raise TypeError(
                "Preferences with profiles should be passed as"
                " tuple of two DataFrames")


def _check_full_veto(strong_veto: bool):
    if not isinstance(strong_veto, bool):
        raise TypeError("Full veto should be a boolean value")


def _check_minimum_interaction_effect(minimum_interaction_effect: bool):
    if not isinstance(minimum_interaction_effect, bool):
        raise TypeError(
            "Minimum interaction effect should be a boolean value")


def discordance_validation(criteria: List[str], partial_preferences: Union[
    pd.DataFrame, Tuple[pd.DataFrame]],
                           tau: NumericValue, decimal_place: NumericValue,
                           preferences: Union[
                               pd.DataFrame, Tuple[pd.DataFrame]],
                           categories_profiles: bool):
    """
    Validates input data for Discordance calculation.

    :param tau: technical parameter, τ ∈ [1, k], smaller τ → weaker
     discordance
    :param decimal_place: with this you can choose the decimal_place of
     the output numbers
    :param preferences: if not empty function returns already calculated
     preference instead of just discordance
    :param criteria: list of criteria names
    :param partial_preferences: partial preference of every alternative over
     other alternatives or profiles
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


def veto_validation(alternatives_performances: pd.DataFrame,
                    weights: pd.Series, veto_thresholds: pd.Series,
                    directions: pd.Series, full_veto: bool,
                    profiles_performance: pd.DataFrame,
                    decimal_place: NumericValue,
                    preferences: Union[pd.DataFrame, Tuple[pd.DataFrame]]):
    _check_weights(weights)
    criteria = weights.index
    _check_performances(alternatives_performances, criteria)
    _check_veto_thresholds(veto_thresholds, criteria)
    _check_directions(directions, criteria)
    _check_full_veto(full_veto)
    _check_decimal_place(decimal_place)
    if profiles_performance is not None:
        _check_performances(profiles_performance, criteria)
    if preferences is not None:
        _check_preferences(preferences)
