"""
This module implements clustering method based on PrometheeTri and k-mean
algorithm.
"""
from typing import Tuple
import numpy as np
import core.preference_commons as pc
from core.clusters_commons import group_alternatives, calculate_new_profiles
from core.input_validation import promethee_cluster_validation
from modular_parts.sorting import calculate_prometheetri_sorted_alternatives
import pandas as pd
import random
from modular_parts.preference.M3_PrometheePreference import \
    compute_preference_indices

__all__ = ['promethee_cluster']


def promethee_cluster(alternatives_performances: pd.DataFrame,
                      preference_thresholds: pd.Series,
                      indifference_thresholds: pd.Series,
                      s_parameters: pd.Series,
                      generalized_criteria: pd.Series,
                      directions: pd.Series,
                      weights: pd.Series,
                      n_categories: int) -> pd.Series:
    """
    Divides alternatives into k clusters using k-mean algorithm and
    PrometheeTri.

    :param alternatives_performances: DataFrame of alternatives' performances
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param s_parameters: s parameter for each criterion
    :param generalized_criteria: list of preference functions
    :param directions: directions of preference of criteria
    :param weights: criteria with weights
    :param n_categories: Number of categories

    :return: alternatives grouped into k ordered clusters
    """
    promethee_cluster_validation(alternatives_performances,
                                 preference_thresholds,
                                 indifference_thresholds,
                                 s_parameters,
                                 generalized_criteria,
                                 directions,
                                 weights,
                                 n_categories)
    alternatives_performances = pc.directed_alternatives_performances(
        alternatives_performances, directions)
    categories = pd.Index([f'C{i}' for i in range(1, n_categories + 1)])
    if n_categories > alternatives_performances.index.__len__():
        raise Exception("Number of cluster must be smaller "
                        "then number of alternatives!")

    profiles = alternatives_performances.iloc[
        random.sample(range(0, alternatives_performances.index.__len__()),
                      n_categories)]
    profiles.index = categories
    old_assignment = pd.Series([], dtype=pd.StringDtype())
    assignment, profiles = _calculate_sorted_alternatives(
        alternatives_performances, preference_thresholds,
        indifference_thresholds, s_parameters, generalized_criteria,
        directions, weights, profiles)
    while not old_assignment.equals(assignment):
        old_assignment = assignment.copy()
        assignment, profiles = _calculate_sorted_alternatives(
            alternatives_performances, preference_thresholds,
            indifference_thresholds, s_parameters,
            generalized_criteria, directions, weights, profiles)

    cluster = group_alternatives(assignment)
    cluster.sort_values(key=lambda x: x.str.len(), inplace=True)
    return cluster


def _calculate_sorted_alternatives(alternatives_performances: pd.DataFrame,
                                   preference_thresholds: pd.Series,
                                   indifference_thresholds: pd.Series,
                                   s_parameters: pd.Series,
                                   generalized_criteria: pd.Series,
                                   directions: pd.Series, weights: pd.Series,
                                   profiles: pd.DataFrame) -> Tuple[
    pd.Series, pd.DataFrame]:
    """
    This function calculates new partial preferences, applies PrometheeTri
    and sort alternatives into categories.

    :param alternatives_performances: DataFrame of alternatives' performances
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param s_parameters: s parameter for each criterion
    :param generalized_criteria: list of preference functions
    :param directions: directions of preference of criteria
    :param weights: criteria with weights
    :param n_categories: Number of categories

    :return: Alternatives assignment, redefined profiles_performances

    """
    _, partial_prefe = compute_preference_indices(alternatives_performances,
                                                  preference_thresholds,
                                                  indifference_thresholds,
                                                  s_parameters,
                                                  generalized_criteria,
                                                  directions, weights,
                                                  profiles)

    _, profile_partial_pref = compute_preference_indices(
        profiles, preference_thresholds, indifference_thresholds,
        s_parameters, generalized_criteria, directions, weights)

    assignment = calculate_prometheetri_sorted_alternatives(
        profiles.index.tolist(), weights, partial_prefe,
        profile_partial_pref, True)

    profiles_return = calculate_new_profiles(
        profiles, alternatives_performances, assignment, np.median)

    return assignment, profiles_return