import numpy
from pandas._libs.internals import defaultdict
import core.preference_commons as pc
from core.clusters_commons import group_alternatives, _calculate_new_profiles
from modular_parts.sorting import calculate_prometheetri_sorted_alternatives
import pandas as pd
import random
from modular_parts.preference.M3_PrometheePreference import *

__all__ = ['promethee_cluster']


def promethee_cluster(alternatives_performances: pd.DataFrame,
                      preference_thresholds: pd.Series,
                      indifference_thresholds: pd.Series,
                      standard_deviations: pd.Series,
                      generalized_criteria: pd.Series,
                      directions: pd.Series,
                      weights: pd.Series,
                      number_of_clusters: int) -> pd.Series:
    """
    Cluster the alternatives using k-mean algorithm and PrometheeTri.

    :param alternatives_performances: DataFrame of alternatives' performances.
    :param preference_thresholds: Series of preference thresholds.
    :param indifference_thresholds: Series of indifference thresholds.
    :param standard_deviations: Series of standard deviations.
    :param generalized_criteria: Series of generalized criteria.
    :param directions: Series of directions.
    :param weights: Series of weights.
    :param number_of_clusters: Number of categories

    :return: Tuple containing Series with the cluster labels and grouped alternatives data."""

    alternatives_performances = pc.directed_alternatives_performances(alternatives_performances, directions)
    categories = pd.Index([f'C{i}' for i in range(1, number_of_clusters + 1)])
    if number_of_clusters > alternatives_performances.index.__len__():
        raise Exception("Number of cluster must be smaller then number of alternatives!")

    profiles = alternatives_performances.iloc[
        random.sample(range(0, alternatives_performances.index.__len__()), number_of_clusters)]
    profiles.index = categories
    old_assignment = pd.Series([], dtype=pd.StringDtype())
    assignment, profiles = _calculate_sorted_alternatives(alternatives_performances, preference_thresholds,
                                                          indifference_thresholds, standard_deviations,
                                                          generalized_criteria, directions, weights,
                                                          profiles)
    while not old_assignment.equals(assignment):
        old_assignment = assignment.copy()
        assignment, profiles = _calculate_sorted_alternatives(alternatives_performances, preference_thresholds,
                                                              indifference_thresholds, standard_deviations,
                                                              generalized_criteria, directions, weights,
                                                              profiles)

    cluster = group_alternatives(assignment)
    cluster.sort_values(key=lambda x: x.str.len(), inplace=True)
    return cluster


def _calculate_sorted_alternatives(alternatives_performances, preference_thresholds,
                                   indifference_thresholds, standard_deviations,
                                   generalized_criteria, directions, weights,
                                   profiles):
    """
    Calculates new partial preferences, applies PrometheeTri and redefines new clusters.

    :return: Alternatives assignment, Redefined central_profiles

    """
    _, partial_prefe = compute_preference_indices(alternatives_performances, preference_thresholds,
                                                  indifference_thresholds, standard_deviations,
                                                  generalized_criteria, directions, weights,
                                                  profiles)

    _, profile_partial_pref = compute_preference_indices(profiles, preference_thresholds,
                                                         indifference_thresholds, standard_deviations,
                                                         generalized_criteria, directions, weights)

    assignment = calculate_prometheetri_sorted_alternatives(profiles.index.tolist(), weights, (partial_prefe),
                                                            profile_partial_pref, True)

    profiles_return = _calculate_new_profiles(profiles, alternatives_performances, assignment, numpy.median)

    return assignment, profiles_return
