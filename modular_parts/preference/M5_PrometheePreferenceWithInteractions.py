"""
This module calculates preference indices with interactions between criteria.
"""
from typing import Tuple, Union
from core.aliases import NumericValue
import core.preference_commons as pc
import pandas as pd

__all__ = ["compute_preference_indices_with_interactions"]

from core.input_validation import promethee_interaction_preference_validation


def compute_preference_indices_with_interactions(
        alternatives_performances: pd.DataFrame,
        weights: pd.Series,
        preference_thresholds: pd.Series,
        indifference_thresholds: pd.Series,
        s_parameters: pd.Series,
        generalized_criteria: pd.Series,
        directions: pd.Series,
        interactions: pd.DataFrame,
        profiles_performance: pd.DataFrame = None,
        decimal_place: NumericValue = 3,
        minimum_interaction_effect: bool = False) -> Union[
    Tuple[pd.DataFrame, pd.DataFrame], Tuple[
        Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]]:
    """
    Calculates preference of every alternative over other alternatives
    or profiles based on partial preferences. Includes interactions between
    criteria effect.

    :param alternatives_performances: Dataframe of alternatives' value at
    every criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param s_parameters: s parameter for each criterion
    :param generalized_criteria: list of preference functions
    :param directions: directions of preference of criteria
    :param weights: criteria with weights
    :param interactions: DataFrame of interactions between criteria with
     coefficients
    :param profiles_performance: Dataframe of profiles performance (value)
    at every criterion
    :param decimal_place: the decimal place of the output numbers
    :param minimum_interaction_effect: boolean representing function used to
     capture the interaction effects in the ambiguity zone. DM can choose 2
     different functions: minimum (true) or multiplication (false)
    :return: preferences and partial preferences
    """
    promethee_interaction_preference_validation(alternatives_performances,
                                                preference_thresholds,
                                                indifference_thresholds,
                                                s_parameters,
                                                generalized_criteria,
                                                directions, weights,
                                                profiles_performance,
                                                interactions,
                                                minimum_interaction_effect,
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
        criteria=criteria, preference_thresholds=preference_thresholds,
        indifference_thresholds=indifference_thresholds,
        s_parameters=s_parameters,
        generalized_criteria=generalized_criteria,
        categories_profiles=categories_profiles,
        alternatives_performances=alternatives_performances,
        profile_performance_table=profile_performance_table)
    if categories_profiles is None:
        return _preferences(minimum_interaction_effect, interactions, weights,
                            criteria, partialPref, decimal_place,
                            alternatives
                            ), partialPref
    else:
        return (
                   _preferences(minimum_interaction_effect, interactions,
                                weights,
                                criteria, partialPref[0], decimal_place,
                                alternatives, categories_profiles),
                   _preferences(minimum_interaction_effect, interactions,
                                weights,
                                criteria, partialPref[1], decimal_place,
                                categories_profiles, alternatives)
               ), partialPref


def _preferences(minimum_interaction_effect: bool,
                 interactions: pd.DataFrame, weights: pd.Series,
                 criteria: pd.Index, partialPref: pd.DataFrame,
                 decimal_place: NumericValue, i_iter: pd.Index,
                 j_iter: pd.Index = None) -> pd.DataFrame:
    """
    Calculates aggregated preference indices.

    :param minimum_interaction_effect: boolean representing function used to
     capture the interaction effects in the ambiguity zone.
    :param interactions: DataFrame of interactions between criteria with
     coefficients
    :param weights: criteria with weights
    :param criteria: list of criteria
    :param partialPref: partial preference indices
    :param decimal_place: the decimal place of the output numbers
    :param i_perf: alternatives or categories profiles performances
    :param j_perf: alternatives or categories profiles performances or None

    :return: aggregated preference indices
    """
    if j_iter is None:
        j_iter = i_iter
    preferences = []
    for i in i_iter:
        aggregatedPI = []
        for j in j_iter:
            Pi_A_B = 0
            interaction_ab = 0
            for k in criteria:
                Pi_A_B += partialPref.loc[k, i][j] * weights[k]
            for key in interactions.index.values:
                k1 = interactions['criterion_1'].loc[key]
                k2 = interactions['criterion_2'].loc[key]
                coefficient = interactions['coefficient'].loc[key] * (
                    1 if interactions['type'].loc[key].value > 0 else -1)
                if interactions['type'].loc[key].value == -1:
                    interaction_ab += _interaction_effects(
                        minimum_interaction_effect, partialPref.loc[k1, i][j],
                        partialPref.loc[k2, j][i]) * coefficient
                else:
                    interaction_ab += _interaction_effects(
                        minimum_interaction_effect, partialPref.loc[k1, i][j],
                        partialPref.loc[k2, i][j]) * coefficient

            aggregated = round((Pi_A_B + interaction_ab) / (
                    sum(weights.values) + interaction_ab), decimal_place)
            aggregatedPI.append(aggregated if aggregated >= 0 else 0)
        preferences.append(aggregatedPI)
    preferences = pd.DataFrame(data=preferences, columns=j_iter, index=i_iter)
    return preferences


def _interaction_effects(minimum_interaction_effect: bool, pi: NumericValue,
                         pj: NumericValue) -> NumericValue:
    """
    Calculates Function Z - used to capture the interaction effects in the
    ambiguity zone

    :param minimum_interaction_effect: boolean representing function used to
     capture the interaction effects in the ambiguity zone.
    :param pi: partial pref index
    :param pj: partial pref index
    """
    if not minimum_interaction_effect:
        return pi * pj
    else:
        return min(pi, pj)
