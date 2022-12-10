"""
This module implements the basic way of calculating preference indices with
Promethee Preference method.
"""
from core.aliases import NumericValue
import core.preference_commons as pc
from core.input_validation import promethee_preference_validation
import pandas as pd

__all__ = ["compute_preference_indices"]


def compute_preference_indices(alternatives_performances: pd.DataFrame,
                               preference_thresholds: pd.Series,
                               indifference_thresholds: pd.Series,
                               s_parameters: pd.Series,
                               generalized_criteria: pd.Series,
                               directions: pd.Series,
                               weights: pd.Series,
                               profiles_performance: pd.DataFrame = None,
                               decimal_place: NumericValue = 3) -> tuple:
    """
    Calculates preference of every alternative over other alternatives
    or profiles based on partial preferences.
    
    :param alternatives_performances: Dataframe of alternatives' value at
    every criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param s_parameters: s parameter for each criterion
    :param generalized_criteria: list of preference functions
    :param directions: directions of preference of criteria
    :param weights: criteria with weights
    :param profiles_performance: Dataframe of profiles performance (value)
    at every criterion
    :param decimal_place: the decimal place of the output numbers

    :return: preferences and partial preferences
    """
    promethee_preference_validation(alternatives_performances,
                                    preference_thresholds,
                                    indifference_thresholds,
                                    s_parameters,
                                    generalized_criteria, directions,
                                    weights, profiles_performance,
                                    decimal_place)

    alternatives = alternatives_performances.index
    criteria = weights.index

    alternatives_performances = pc.directed_alternatives_performances(
        alternatives_performances, directions)
    if profiles_performance is not None:
        categories_profiles = profiles_performance.index
        profile_performance_table = pc.directed_alternatives_performances(
            profiles_performance, directions)
    else:
        categories_profiles = None
        profile_performance_table = None

    partialPref = pc.partial_preference(
        criteria=criteria,
        preference_thresholds=preference_thresholds,
        indifference_thresholds=indifference_thresholds,
        s_parameters=s_parameters,
        generalized_criteria=generalized_criteria,
        categories_profiles=categories_profiles,
        alternatives_performances=alternatives_performances,
        profile_performance_table=profile_performance_table)
    if categories_profiles is None:
        return _preferences(weights, criteria, decimal_place, partialPref,
                            alternatives), partialPref
    else:
        return (_preferences(weights, criteria, decimal_place, partialPref[0],
                             alternatives, categories_profiles),
                _preferences(weights, criteria, decimal_place, partialPref[1],
                             categories_profiles, alternatives)
                ), partialPref


def _preferences(weights: pd.Series, criteria: pd.Index,
                 decimal_place: NumericValue, partialPref: pd.DataFrame,
                 i_iter: pd.Index, j_iter: pd.Index = None) -> pd.DataFrame:
    """
    Calculates aggregated preference indices.

    :param weights: criteria with weights
    :param criteria: list of criteria
    :param decimal_place: the decimal place of the output numbers
    :param partialPref: partial preference indices
    :param i_iter: alternatives or categories profiles
    :param j_iter: alternatives or categories profiles or None

    :return: aggregated preference indices
    """
    weight_sum = sum(weights.values)
    if j_iter is None:
        j_iter = i_iter
    preferences = []
    for i in i_iter:
        aggregatedPI = []
        for j in j_iter:
            Pi_A_B = 0
            for k in criteria:
                Pi_A_B += partialPref.loc[k, i][j] * weights[k]
            Pi_A_B = Pi_A_B / weight_sum
            aggregatedPI.append(round(Pi_A_B, decimal_place))
        preferences.append(aggregatedPI)

    preferences = pd.DataFrame(data=preferences, columns=j_iter, index=i_iter)
    return preferences
