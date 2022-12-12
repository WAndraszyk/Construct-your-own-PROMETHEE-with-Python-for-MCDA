from typing import List, Union, Tuple

import pandas as pd
from core.aliases import NumericValue
from core.enums import Direction, InteractionType
from core.enums import GeneralCriterion

__all__ = ["promethee_preference_validation",
           "reinforced_preference_validation", "discordance_validation",
           "promethee_interaction_preference_validation", "veto_validation"]


def _check_performances_with_criteria(performances: pd.DataFrame,
                                      criteria: pd.Index):
    """
    Check if performances are valid.

    :param performances: pd.DataFrame with alternatives/profiles as index
    and criteria as columns
    :param criteria: pd.Index with criteria names
    :raise ValueError: if performances are not valid
    """

    # Check if performances are a DataFrame
    if not isinstance(performances, pd.DataFrame):
        raise ValueError("Performances should be passed "
                         "as a DataFrame")

    # Check if performances are numeric
    if not performances.dtypes.values.all() in ['int32',
                                                'int64',
                                                'float32',
                                                'float64']:
        raise ValueError("Performances should be passed "
                         "with int or float values")

    # Check if performances have the same criteria as other object
    _check_if_criteria_are_the_same(performances.columns, criteria)


def _check_preference_thresholds(preference_thresholds: pd.Series,
                                 criteria: pd.Index):
    """
    Check if preference thresholds are valid.

    :param preference_thresholds: pd.Series with criteria as index and
    preference thresholds as values
    :param criteria: pd.Index with criteria names
    :raise ValueError: if preference thresholds are not valid
    """

    # Check if preference thresholds are a Series
    if not isinstance(preference_thresholds, pd.Series):
        raise TypeError("Preference thresholds should be passed as "
                        "a Series object")

    _check_if_criteria_are_the_same(preference_thresholds.index, criteria)

    # Check if preference thresholds are numeric
    for threshold in preference_thresholds:
        if not (isinstance(threshold, int) or isinstance(threshold, float)
                or threshold is None):
            raise TypeError("Preference thresholds should be numeric values"
                            " or None")

    # Check if preference thresholds are not negative
    if (preference_thresholds < 0).any():
        raise ValueError("Preference thresholds can not be lower than 0")


def _check_indifference_thresholds(indifference_thresholds: pd.Series,
                                   criteria: pd.Index):
    """
    Check if indifference thresholds are valid.

    :param indifference_thresholds: pd.Series with criteria as index and
    indifference thresholds as values
    :param criteria: pd.Index with criteria names
    :raise ValueError: if indifference thresholds are not valid
    """

    # Check if indifference thresholds are a Series
    if not isinstance(indifference_thresholds, pd.Series):
        raise TypeError("Indifference thresholds should be passed as a "
                        "Series object")

    _check_if_criteria_are_the_same(indifference_thresholds.index, criteria)

    # Check if indifference thresholds are numeric or None
    for threshold in indifference_thresholds:
        if not (isinstance(threshold, int) or isinstance(threshold, float)
                or threshold is None):
            raise TypeError("Indifference thresholds should be numeric values"
                            " or None")

    # Check if indifference thresholds are not negative
    if (indifference_thresholds < 0).any():
        raise ValueError("Indifference thresholds can not be lower than 0")


def _check_standard_deviations(standard_deviations: pd.Series,
                               criteria: pd.Index):
    """
    Check if standard deviations are valid.

    :param standard_deviations: pd.Series with criteria as index and
    standard deviations as values
    :param criteria: pd.Index with criteria names
    :raise ValueError: if standard deviations are not valid
    """

    # Check if standard deviations are a Series
    if not isinstance(standard_deviations, pd.Series):
        raise TypeError("Standard deviations should be passed as a "
                        "Series object")

    _check_if_criteria_are_the_same(standard_deviations.index, criteria)

    # Check if standard deviations thresholds are numeric
    for deviation in standard_deviations:
        if not (isinstance(deviation, int) or isinstance(deviation, float)
                or deviation is None):
            raise TypeError("Standard deviations should be numeric values"
                            " or None")

    # Check if standard deviations are not negative
    if (standard_deviations < 0).any():
        raise ValueError("Standard deviations can not be lower than 0")


def _check_veto_thresholds(veto_thresholds: pd.Series, criteria: pd.Index):
    """
    Check if veto thresholds are valid.

    :param veto_thresholds: pd.Series with criteria as index and
    veto thresholds as values
    :param criteria: pd.Index with criteria names
    :raise ValueError: if veto thresholds are not valid
    """

    # Check if veto thresholds are a Series
    if not isinstance(veto_thresholds, pd.Series):
        raise TypeError("Veto thresholds should be passed as a "
                        "Series object")

    _check_if_criteria_are_the_same(veto_thresholds.index, criteria)

    # Check if veto thresholds are numeric
    for threshold in veto_thresholds:
        if not (isinstance(threshold, int) or isinstance(threshold, float)
                or threshold is None):
            raise TypeError("Veto thresholds should be numeric values"
                            " or None")

    # Check if veto thresholds are not negative
    if (veto_thresholds < 0).any():
        raise ValueError("Veto thresholds can not be lower than 0")


def _check_generalized_criteria(generalized_criteria: pd.Series,
                                criteria: pd.Index):
    """
    Check if generalized criteria are valid.

    :param generalized_criteria: pd.Series with criteria as index and
    Generalized criteria enums as values
    :param criteria: pd.Index with criteria names
    :raise ValueError: if generalized criteria are not valid
    """

    # Check if generalized criteria are a Series
    if not isinstance(generalized_criteria, pd.Series):
        raise TypeError("Generalized criteria should be passed as a "
                        "Series object")

    _check_if_criteria_are_the_same(generalized_criteria.index, criteria)

    # Check if generalized criteria are GeneralCriterion enums
    if not all(isinstance(criterion, GeneralCriterion)
               for criterion in generalized_criteria):
        raise TypeError("Generalized criteria should be GeneralizedCriteria "
                        "enums")


def _check_directions(directions: pd.Series, criteria: pd.Index):
    """
    Check if directions are valid.

    :param directions: pd.Series with criteria as index and Direction enums
    as values
    :param criteria: pd.Index with criteria names
    :raise ValueError: if directions are not valid
    """

    # Check if directions are a Series
    if not isinstance(directions, pd.Series):
        raise TypeError("Directions should be passed as a Series object")

    _check_if_criteria_are_the_same(directions.index, criteria)

    # Check if directions are Direction enums
    if not all(isinstance(direction, Direction) for direction in directions):
        raise TypeError("Directions should be Direction enums")


def _check_weights(weights: pd.Series):
    """
    Check if weights are valid.

    :param weights: pd.Series with criteria as index and weights as values
    :raises ValueError: if weights are not valid
    """

    # Check if weights are a Series
    if not isinstance(weights, pd.Series):
        raise ValueError("Criteria weights should be passed as a"
                         " Series object")

    # Check if weights are numeric
    if weights.dtype not in ['int32', 'int64', 'float32', 'float64']:
        raise ValueError("Weights should be a numeric values")

    # Check if all weights are positive
    if (weights <= 0).any():
        raise ValueError("Weights should be positive")


def _check_decimal_place(decimal_place: int):
    """
    Check if decimal place is valid.

    :param decimal_place: integer with decimal place
    :raises ValueError: if decimal place is not valid
    """

    # Check if decimal place is an integer
    if not isinstance(decimal_place, int):
        raise TypeError("Decimal place must be integer")

    # Check if decimal place is not negative
    if decimal_place < 0:
        raise ValueError("Decimal place must be not negative")


def _check_if_criteria_are_the_same(criteria_1: pd.Index,
                                    criteria_2: pd.Index):
    """
    Check if two criteria are the same.

    :param criteria_1: pd.Index with criteria names
    :param criteria_2: pd.Index with criteria names
    :raises ValueError: if criteria are not the same
    """

    # Check if criteria are the same
    if not criteria_1.equals(criteria_2):
        raise ValueError("Criteria are not the same in different objects")


def promethee_preference_validation(alternatives_performances: pd.DataFrame,
                                    preference_thresholds: pd.Series,
                                    indifference_thresholds: pd.Series,
                                    standard_deviations: pd.Series,
                                    generalized_criteria: pd.Series,
                                    directions: pd.Series,
                                    criteria_weights: pd.Series,
                                    profiles_performance: pd.DataFrame,
                                    decimal_place: NumericValue):
    """
    Check if all inputs are valid for PROMETHEE Preference method.

    :param alternatives_performances: pd.DataFrame with alternatives as index
    and criteria as columns
    :param preference_thresholds: pd.Series with criteria as index and
    preference thresholds as values
    :param indifference_thresholds: pd.Series with criteria as index and
    indifference thresholds as values
    :param standard_deviations: pd.Series with criteria as index and
    standard deviations as values
    :param generalized_criteria: pd.Series with criteria as index and
    General criterion enums as values
    :param directions: pd.Series with criteria as index and Direction enums
    as values
    :param criteria_weights: pd.Series with criteria as index and weights as
    values
    :param profiles_performance: pd.DataFrame with profiles as index and
    criteria as columns
    :param decimal_place: integer with decimal place
    :raises ValueError: if input data is not valid
    """
    _check_weights(criteria_weights)
    criteria = criteria_weights.index
    _check_performances_with_criteria(alternatives_performances, criteria)
    _check_preference_thresholds(preference_thresholds, criteria)
    _check_indifference_thresholds(indifference_thresholds, criteria)
    _check_standard_deviations(standard_deviations, criteria)
    _check_generalized_criteria(generalized_criteria, criteria)
    _check_directions(directions, criteria)
    _check_decimal_place(decimal_place)
    if profiles_performance is not None:
        _check_performances_with_criteria(profiles_performance, criteria)


def promethee_interaction_preference_validation(
        alternatives_performances: pd.DataFrame,
        preference_thresholds: pd.Series,
        indifference_thresholds: pd.Series,
        standard_deviations: pd.Series,
        generalized_criteria: pd.Series,
        directions: pd.Series,
        criteria_weights: pd.Series,
        profiles_performance: pd.DataFrame,
        interactions: pd.DataFrame,
        minimum_interaction_effect: bool,
        decimal_place: NumericValue):
    """
    Check if all inputs are valid for PROMETHEE Interaction Preference method.

    :param alternatives_performances: pd.DataFrame with alternatives as index
    and criteria as columns
    :param preference_thresholds: pd.Series with criteria as index and
    preference thresholds as values
    :param indifference_thresholds: pd.Series with criteria as index and
    indifference thresholds as values
    :param standard_deviations: pd.Series with criteria as index and
    standard deviations as values
    :param generalized_criteria: pd.Series with criteria as index and
    General criterion enums as values
    :param directions: pd.Series with criteria as index and Direction enums
    as values
    :param criteria_weights: pd.Series with criteria as index and weights as
    values
    :param profiles_performance: pd.DataFrame with profiles as index and
    criteria as columns
    :param interactions: pd.DataFrame with interactions as index and
    'criterion_1', 'criterion_2', 'type' and 'coefficient' columns
    :param minimum_interaction_effect: boolean representing function used to
     capture the interaction effects in the ambiguity zone
    :param decimal_place: integer with decimal place
    :raise ValueError: if input data is not valid
    """
    _check_weights(criteria_weights)
    criteria = criteria_weights.index
    _check_performances_with_criteria(alternatives_performances, criteria)
    _check_preference_thresholds(preference_thresholds, criteria)
    _check_indifference_thresholds(indifference_thresholds, criteria)
    _check_standard_deviations(standard_deviations, criteria)
    _check_generalized_criteria(generalized_criteria, criteria)
    _check_directions(directions, criteria)
    _check_decimal_place(decimal_place)
    _check_interactions(interactions, criteria)
    _check_minimum_interaction_effect(minimum_interaction_effect)
    if profiles_performance is not None:
        _check_performances_with_criteria(profiles_performance, criteria)


def _check_interactions(interactions: pd.DataFrame, criteria: pd.Index):
    """
    Check if interactions are valid.

    :param interactions: pd.DataFrame with interactions as index and
    'criterion_1', 'criterion_2', 'type' and 'coefficient' columns
    :param criteria: pd.Index with criteria names
    :raises ValueError: if interactions are not valid
    """

    # Check if interactions are DataFrame
    if not isinstance(interactions, pd.DataFrame):
        raise TypeError(
            "Performances on criteria should be passed as a DataFrame object")

    _check_interaction_columns(interactions.columns)
    _check_interactions_criteria(interactions['criterion_1'], criteria)
    _check_interactions_criteria(interactions['criterion_2'], criteria)
    _check_interactions_types(interactions['type'])
    _check_interaction_coefficient(interactions[['type', 'coefficient']])


def _check_interaction_columns(column_names: pd.Index):
    """
    Check if interactions columns are valid.

    :param column_names: pd.Index with interactions columns names
    :raises TypeError: if interactions columns are not valid
    """

    # Check if interactions columns have proper names
    if column_names.values.tolist() != ['criterion_1', 'criterion_2', 'type',
                                        'coefficient']:
        raise TypeError(
            "Interactions columns should be names as 'criterion_1', "
            "'criterion_2', 'type', 'coefficient'")


def _check_interactions_criteria(columns: pd.Series, criteria: pd.Index):
    """
    Check if interactions criteria are valid.

    :param columns: pd.Series with interactions criteria
    :param criteria: pd.Index with criteria names
    :raises TypeError: if interactions criteria are not valid
    """

    # Check if criteria in interactions are valid
    for value in columns:
        if value not in criteria.values:
            raise TypeError("Criteria names in interactions are not valid!")


def _check_interactions_types(interactions: pd.Series):
    """
    Check if interactions types are valid.

    :param interactions: pd.Series with InteractionType enums as values
    :raises ValueError: if interactions types are not valid
    """

    # Check if interactions types are InteractionType enums
    if not all([isinstance(value, InteractionType) for value in
                interactions.values]):
        raise ValueError("Interaction types should be "
                         "of InteractionType enum")


def _check_interaction_coefficient(interactions: pd.DataFrame):
    """
    Check if interactions coefficients are valid.

    :param interactions: pd.DataFrame with interactions and
    'interaction_type' and 'coefficient' columns
    :raises TypeError: if interactions coefficients are not valid
    """
    for _, row in interactions.iterrows():
        if row['type'] is InteractionType.WKN:
            if row['coefficient'] > 0:
                raise TypeError("Mutual weakening coefficient must be"
                                " less than 0")
        elif row['coefficient'] < 0:
            raise TypeError(
                "Mutual antagonistic and strengthening "
                "coefficients must be greater than 0")


def _check_reinforced_preference_thresholds(
        reinforced_preference_thresholds: pd.Series, criteria: pd.Index):
    """
    Check if reinforced preference thresholds are valid.

    :param reinforced_preference_thresholds: pd.Series with criteria as index
    and reinforced preference thresholds as values
    :param criteria: pd.Index with criteria names
    :raises ValueError: if reinforced preference thresholds are not valid
    :raises TypeError: if reinforced preference thresholds are not valid
    """

    # Check if reinforced preference thresholds are Series
    if not isinstance(reinforced_preference_thresholds, pd.Series):
        raise TypeError(
            "Reinforced preference thresholds should"
            " be passed as a Series object")

    _check_if_criteria_are_the_same(reinforced_preference_thresholds.index,
                                    criteria)

    # Check if reinforced preference thresholds are numeric
    for threshold in reinforced_preference_thresholds:
        if not (isinstance(threshold, int) or isinstance(threshold, float)
                or threshold is None):
            raise TypeError("Reinforced preference thresholds"
                            " should be numeric values or None")

    # Check if reinforced preference thresholds are not negative
    if (reinforced_preference_thresholds < 0).any():
        raise ValueError("Reinforced preference thresholds"
                         " can not be lower than 0")


def _check_reinforcement_factors(reinforcement_factors: pd.Series,
                                 criteria: pd.Index):
    """
    Check if reinforcement factors are valid.

    :param reinforcement_factors: pd.Series with criteria as index
    and reinforcement factors as values
    :param criteria: pd.Index with criteria names
    :raises ValueError: if reinforcement factors are not valid
    :raises TypeError: if reinforcement factors are not valid
    """

    # Check if reinforcement factors are Series
    if not isinstance(reinforcement_factors, pd.Series):
        raise TypeError(
            "Reinforcement factors should be passed as a Series object")

    _check_if_criteria_are_the_same(reinforcement_factors.index, criteria)

    # Check if reinforced factors are numeric
    if reinforcement_factors.dtype not in ['int32', 'int64',
                                           'float32', 'float64']:
        raise ValueError("Reinforced factors should be a numeric values")

    # Check if reinforcement factors are greater than 1
    if (reinforcement_factors < 1).any():
        raise ValueError("Reinforcement factores must be grater than 1")


def reinforced_preference_validation(
        alternatives_performances: pd.DataFrame,
        preference_thresholds: pd.Series,
        indifference_thresholds: pd.Series,
        generalized_criteria: pd.Series,
        directions: pd.Series,
        reinforced_preference_thresholds: pd.Series,
        reinforcement_factors: pd.Series,
        criteria_weights: pd.Series,
        profiles_performance: pd.DataFrame,
        decimal_place: NumericValue):
    """
    Check if all inputs are valid for PROMETHEE Reinforced Preference method
    
    :param alternatives_performances: pd.DataFrame with alternatives as index
    and criteria as columns
    :param preference_thresholds: pd.Series with criteria as index and
    preference thresholds as values
    :param indifference_thresholds: pd.Series with criteria as index and
    indifference thresholds as values
    :param generalized_criteria: pd.Series with criteria as index and
    generalized criteria as values
    :param directions: pd.Series with criteria as index and
    Direction enums as values
    :param reinforced_preference_thresholds: pd.Series with criteria as index
    and reinforced preference thresholds as values
    :param reinforcement_factors: pd.Series with criteria as index
    and reinforcement factors as values
    :param criteria_weights: pd.Series with criteria as index and
    criteria weights as values
    :param profiles_performance: pd.DataFrame with profiles as index and
    criteria as columns
    :param decimal_place: int with number of decimal places
    :raises TypeError: if any input is not valid
    :raises ValueError: if any input is not valid
    """
    _check_weights(criteria_weights)
    criteria = criteria_weights.index
    _check_performances_with_criteria(alternatives_performances, criteria)
    _check_preference_thresholds(preference_thresholds, criteria)
    _check_indifference_thresholds(indifference_thresholds, criteria)
    _check_generalized_criteria(generalized_criteria, criteria)
    _check_directions(directions, criteria)
    _check_reinforced_preference_thresholds(reinforced_preference_thresholds,
                                            criteria)
    _check_reinforcement_factors(reinforcement_factors, criteria)
    _check_decimal_place(decimal_place)
    if profiles_performance is not None:
        _check_performances_with_criteria(profiles_performance, criteria)


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
    _check_performances_with_criteria(alternatives_performances, criteria)
    _check_veto_thresholds(veto_thresholds, criteria)
    _check_directions(directions, criteria)
    _check_full_veto(full_veto)
    _check_decimal_place(decimal_place)
    if profiles_performance is not None:
        _check_performances_with_criteria(profiles_performance, criteria)
    if preferences is not None:
        _check_preferences(preferences)
