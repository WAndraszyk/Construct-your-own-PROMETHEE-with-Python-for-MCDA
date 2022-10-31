from enum import Enum
from core.aliases import NumericValue, PerformanceTable
from typing import List
import core.preference_commons as pc
import pandas as pd

__all__ = ["compute_preference_indices_with_integrations"]


def compute_preference_indices_with_integrations(
        alternatives_performances: PerformanceTable,
        weights: pd.Series,
        preference_thresholds: pd.Series,
        indifference_thresholds: pd.Series,
        standard_deviations: pd.Series,
        generalized_criteria: pd.Series,
        directions: pd.Series,
        interactions: PerformanceTable,
        interaction_effects_fuction: int = 0,
        profiles_performance: PerformanceTable = None,
        decimal_place: NumericValue = 3,
        z_function: NumericValue = 0):
    """
    Calculates preference of every alternative over other alternatives
    or profiles based on partial preferences

    :param alternatives_performances: Dataframe of alternatives' value at every criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param standard_deviations: standard deviation for each criterion
    :param generalized_criteria: list of preference functions
    :param directions: directions of preference of criteria
    :param weights: criteria with weights
    :param interactions: interactions between criteria with coefficient weight
    :param profiles_performance: Dataframe of profiles performance (value) at every criterion
    :param decimal_place: with this you can choose the decimal_place of the output numbers
    :return: preferences
    :return: partial preferences
    """

    alternatives = alternatives_performances.index
    criteria = weights.keys()
    alternatives_performances = pc.directed_alternatives_performances(alternatives_performances, directions)
    if profiles_performance is not None:
        categories_profiles = profiles_performance.keys()
        profile_performance_table = pc.directed_alternatives_performances(profiles_performance, directions)
    else:
        categories_profiles = None
        profile_performance_table = None

    partialPref = pc.partial_preference(criteria=criteria, p_list=preference_thresholds,
                                        q_list=indifference_thresholds, s_list=standard_deviations,
                                        generalized_criteria=generalized_criteria,
                                        categories_profiles=categories_profiles,
                                        alternatives_performances=alternatives_performances,
                                        profile_performance_table=profile_performance_table)
    if categories_profiles is None:
        return _preferences(z_function, interactions, weights, criteria, partialPref, alternatives,
                            decimal_place), partialPref
    else:
        return (_preferences(z_function, interactions, weights, criteria, partialPref[0], alternatives, decimal_place,
                             categories_profiles),
                _preferences(z_function, interactions, weights, criteria, partialPref[1], categories_profiles,
                             decimal_place, alternatives)
                ), partialPref


def _preferences(z_function, interactions, weights, criteria, partialPref, alternatives, decimal_place,
                 categories_profiles=None):
    if categories_profiles is None:
        categories_profiles = alternatives
    preferences = []
    for i in alternatives:
        aggregatedPI = []
        for j in categories_profiles:
            Pi_A_B = 0
            interaction_ab = 0
            for k in criteria:
                Pi_A_B += partialPref.loc[k, i][j] * weights[k]
            for key in interactions.index.values:
                k1 = interactions['criterion_1'].loc[key]
                k2 = interactions['criterion_2'].loc[key]
                interaction_ab += _z_function(z_function, partialPref.loc[k1, i][j], partialPref.loc[k2, i][j]) * \
                                  interactions['coefficient'].loc[key] * interactions['type'].loc[key].value

            aggregatedPI.append(
                round((Pi_A_B + interaction_ab) / (sum(weights.values) + interaction_ab), decimal_place))
        preferences.append(aggregatedPI)
    preferences = pd.DataFrame(data=preferences, columns=categories_profiles, index=alternatives)
    return preferences


def _z_function(z_function, pi, pj):
    if z_function != 0:
        return pi * pj
    else:
        return min(pi, pj)
