"""
.. image:: prometheePUT_figures/M27.png

This module implements clustering method based on PrometheeTri and k-mean
algorithm.

Implementation and naming of conventions are taken from
:cite:p:`PClusterTri`.
"""


import random
from typing import Tuple, cast

import numpy as np
import pandas as pd

import core.preference_commons as pc
from core.clusters_commons import calculate_new_profiles, group_alternatives
from core.input_validation.clustering import promethee_cluster_validation

from .M3_PrometheePreference import compute_preference_indices
from .M19_PrometheeTri import calculate_prometheetri_sorted_alternatives

__all__ = ["promethee_cluster"]


def promethee_cluster(
    alternatives_performances: pd.DataFrame,
    preference_thresholds: pd.Series,
    indifference_thresholds: pd.Series,
    s_parameters: pd.Series,
    generalized_criteria: pd.Series,
    directions: pd.Series,
    weights: pd.Series,
    n_categories: int,
) -> pd.Series:
    """
    Divides alternatives into k clusters using k-mean algorithm and
    PrometheeTri.

    :param alternatives_performances: Dataframe of alternatives' value at
        every criterion, index: alternatives, columns: criteria
    :param preference_thresholds: Series of preference threshold for
        each criterion, index: criteria
    :param indifference_thresholds: Series of indifference threshold for
        each criterion, index: criteria
    :param s_parameters: Series of s parameter for each criterion, s parameter
        is a threshold used in Gaussian Criterion, it's defined as an
        intermediate value between indifference and preference threshold,
        index: criteria
    :param generalized_criteria: Series with preference functions as values
        and criteria as index
    :param directions: Series with directions of preference as values and
        criteria as index
    :param weights: Series with weights as values and criteria as index
    :param n_categories: Number of categories

    :return: Series with alternatives - values grouped into k ordered
        clusters - indices
    """

    # input data validation
    promethee_cluster_validation(
        alternatives_performances,
        preference_thresholds,
        indifference_thresholds,
        s_parameters,
        generalized_criteria,
        directions,
        weights,
        n_categories,
    )

    # changing values of alternatives' performances according to direction
    # of criterion for further calculations
    alternatives_performances = pc.directed_alternatives_performances(
        alternatives_performances, directions
    )

    categories = pd.Index([f"C{i}" for i in range(1, n_categories + 1)])

    # initialize central profiles_performances by random choosing them from
    # alternatives
    profiles = alternatives_performances.iloc[
        random.sample(range(0, len(alternatives_performances.index)), n_categories)
    ]
    profiles.index = categories

    # sorting alternatives into categories
    old_assignment = pd.Series([], dtype=pd.StringDtype())
    assignment, profiles = _calculate_sorted_alternatives(
        alternatives_performances,
        preference_thresholds,
        indifference_thresholds,
        s_parameters,
        generalized_criteria,
        directions,
        weights,
        profiles,
    )

    # algorithm ends when assignment doesn't change anymore
    while not old_assignment.equals(assignment):
        old_assignment = assignment.copy(deep=True)
        assignment, profiles = _calculate_sorted_alternatives(
            alternatives_performances,
            preference_thresholds,
            indifference_thresholds,
            s_parameters,
            generalized_criteria,
            directions,
            weights,
            profiles,
        )

    # change output from Series with alternatives indices and categories as
    # values to categories indices and alternatives as values
    cluster = group_alternatives(assignment)
    # temporary switch of the indexes for proper sorting
    # (f.e. for strings '2' < '11')
    cluster.index = pd.Index([int(category[1:]) for category in cluster.index])
    cluster.sort_index(inplace=True)
    cluster.index = categories
    return cluster


def _calculate_sorted_alternatives(
    alternatives_performances: pd.DataFrame,
    preference_thresholds: pd.Series,
    indifference_thresholds: pd.Series,
    s_parameters: pd.Series,
    generalized_criteria: pd.Series,
    directions: pd.Series,
    weights: pd.Series,
    profiles_performances: pd.DataFrame,
) -> Tuple[pd.Series, pd.DataFrame]:
    """
    This function calculates new partial preferences, applies PrometheeTri
    and sort alternatives into categories.

    :param alternatives_performances: Dataframe of alternatives' value at
        every criterion, index: alternatives, columns: criteria
    :param preference_thresholds: Series of preference threshold for
        each criterion, index: criteria
    :param indifference_thresholds: Series of indifference threshold for
        each criterion, index: criteria
    :param s_parameters: Series of s parameter for each criterion, s parameter
        is a threshold used in Gaussian Criterion, it's defined as an
        intermediate value between indifference and preference threshold,
        index: criteria
    :param generalized_criteria: Series with preference functions as values
        and criteria as index
    :param directions: Series with directions of preference as values and
        criteria as index
    :param weights: Series with weights as values and criteria as index
    :param profiles_performances: Dataframe of profiles_performances' value at
        every criterion, index: profiles_performances, columns: criteria

    :return: Tuple with Series of alternatives assignment
        and DataFrame of redefined profiles_performances

    """

    # calculating partial preference alternatives over profiles
    _, partial_pref = compute_preference_indices(
        alternatives_performances,
        preference_thresholds,
        indifference_thresholds,
        s_parameters,
        generalized_criteria,
        directions,
        weights,
        profiles_performances,
    )

    # calculating partial preference profiles over profiles
    _, profile_partial_pref = compute_preference_indices(
        profiles_performances,
        preference_thresholds,
        indifference_thresholds,
        s_parameters,
        generalized_criteria,
        directions,
        weights,
    )

    # sorting alternatives into categories
    assignment = calculate_prometheetri_sorted_alternatives(
        profiles_performances.index.tolist(),
        weights,
        cast(Tuple[pd.DataFrame, pd.DataFrame], partial_pref),
        cast(pd.DataFrame, profile_partial_pref),
        True,
    )

    # update central profiles_performances
    profiles_return = calculate_new_profiles(
        profiles_performances, alternatives_performances, assignment, np.median
    )

    return assignment, profiles_return
