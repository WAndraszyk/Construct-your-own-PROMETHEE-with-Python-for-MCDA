"""
This module implements clustering method based on FlowSort and k-mean
algorithm.
"""
import numpy as np
import pandas as pd
import core.preference_commons as pc
from core.enums import FlowType
from core.clusters_commons import group_alternatives, \
    calculate_new_profiles, initialization_of_the_central_profiles
from core.input_validation import promethee_II_ordered_clustering_validation
from core.promethee_check_dominance import check_dominance_condition
from modular_parts.preference import compute_preference_indices
from modular_parts.flows.M8_PrometheeOutrankingFlows import \
    calculate_promethee_outranking_flows
from modular_parts.flows.M9_NetOutrankingFlow import \
    calculate_net_outranking_flows_for_prometheeII

__all__ = ['promethee_II_ordered_clustering']


def promethee_II_ordered_clustering(alternatives_performances: pd.DataFrame,
                                    preference_thresholds: pd.Series,
                                    indifference_thresholds: pd.Series,
                                    s_parameters: pd.Series,
                                    generalized_criteria: pd.Series,
                                    directions: pd.Series,
                                    weights: pd.Series,
                                    n_categories: int,
                                    max_iterations: int = 100) -> pd.Series:
    """
    Divides alternatives into k ordered clusters using k-mean algorithm and
    Promethee II.

    :param alternatives_performances: DataFrame of alternatives' performances
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param s_parameters: s parameter for each criterion
    :param generalized_criteria: list of preference functions
    :param directions: directions of preference of criteria
    :param weights: criteria with weights
    :param n_categories: number of categories
    :param max_iterations: maximum number of iterations

    :return: alternatives grouped into k ordered clusters
    """

    promethee_II_ordered_clustering_validation(alternatives_performances,
                                               preference_thresholds,
                                               indifference_thresholds,
                                               s_parameters,
                                               generalized_criteria,
                                               directions,
                                               weights,
                                               n_categories)
    global sorted_old
    alternatives_performances = pc.directed_alternatives_performances(
        alternatives_performances, directions)
    categories = pd.Index([f'C{i}' for i in range(1, n_categories + 1)])

    central_profiles = initialization_of_the_central_profiles(
        alternatives_performances, categories, directions)
    assignments = _sort_alternatives_to_categories(alternatives_performances,
                                              preference_thresholds,
                                              indifference_thresholds,
                                              s_parameters,
                                              generalized_criteria,
                                              directions, weights,
                                              central_profiles, categories)
    sorted_old = None
    iteration = 0

    while (not sorted.equals(sorted_old)) and iteration < max_iterations:
        iteration += 1
        sorted_old = sorted
        central_profiles = _calculate_new_profiles_mean(
            central_profiles, alternatives_performances, sorted)
        assignments = _sort_alternatives_to_categories(alternatives_performances,
                                                  preference_thresholds,
                                                  indifference_thresholds,
                                                  s_parameters,
                                                  generalized_criteria,
                                                  directions, weights,
                                                  central_profiles,
                                                  categories)

    cluster = group_alternatives(sorted)
    cluster.sort_index(inplace=True)
    return cluster


def _sort_alternatives_to_categories(
        alternatives_performances: pd.DataFrame,
        preference_thresholds: pd.Series,
        indifference_thresholds: pd.Series, standard_deviations: pd.Series,
        generalized_criteria: pd.Series,
        directions: pd.Series, weights: pd.Series,
        central_profiles: pd.DataFrame,
        categories: pd.Index) -> pd.Series:
    """
    This function calculates new partial preferences, Promethee II flows
    and sort alternatives into categories.

    :param alternatives_performances: DataFrame of alternatives' performances
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param s_parameters: s parameter for each criterion
    :param generalized_criteria: list of preference functions
    :param directions: directions of preference of criteria
    :param weights: criteria with weights

    :return: Series with precise assignments of alternatives to categories

    """
    alternatives_preference, _ = compute_preference_indices(
        alternatives_performances, preference_thresholds,
        indifference_thresholds, standard_deviations,
        generalized_criteria, directions, weights, central_profiles)
    profiles_preference, _ = compute_preference_indices(
        central_profiles, preference_thresholds, indifference_thresholds,
        standard_deviations, generalized_criteria, directions, weights)

    prometheeII_flows = calculate_promethee_outranking_flows(
        alternatives_preference, FlowType.PROMETHEE_II,
        profiles_preference)
    prometheeII_flows = calculate_net_outranking_flows_for_prometheeII(
        prometheeII_flows)
    redirected_profiles = pc.directed_alternatives_performances(
        central_profiles, directions)
    check_dominance_condition(directions, redirected_profiles)
    assignments = calculate_flowsort_assignment(categories.tolist(),
                                           prometheeII_flows)
    assignments = _force_alternative_to_empty_category(sorted,
                                                  central_profiles.index)
    return assignments


def _calculate_new_profiles_mean(profiles_performances: pd.DataFrame,
                                 alternatives_performances: pd.DataFrame,
                                 assignment: pd.Series) -> pd.DataFrame:
    """
    This function updates profiles performances on the basis of the
    alternatives belonging to it using math mean function.


    :param profiles_performances: DataFrame of profiles' performances
    :param alternatives_performances: DataFrame of alternatives' performances
    :param assignment: Series with precise assignments of alternatives to
    categories

    :return: DataFrame of updated profiles' performances
    """
    profiles = calculate_new_profiles(profiles_performances,
                                      alternatives_performances,
                                      assignment, np.mean)
    profiles.fillna(0, inplace=True)
    profiles = profiles.apply(lambda x: x.sort_values().values)
    return profiles


def _force_alternative_to_empty_category(sorted: pd.Series,
                                         categories: pd.Index) -> pd.Series:
    """
    In case given category disappear (is empty) during the execution of the
    algorithm, method force randomly chosen alternative to belong to the
    category.


    :param sorted: Series of alternatives grouped into k ordered clusters
    :param categories: Indices of categories

    :return: Redefined assignments without empty categories
    """
    sorted_copy = sorted.copy(deep=True)
    old_value = []
    while True:
        item = sorted_copy.sample()
        unique_category = sorted_copy.unique()
        if list(set(categories.values) - set(unique_category)) == []:
            break
        if item.values in old_value:
            sorted_copy[item.keys()] = np.random.choice(
                list(set(categories) - set(unique_category)))
        else:
            old_value += [np.random.choice(item.values)]
    return sorted_copy


def calculate_flowsort_assignment(categories: pd.Index,
                                  prometheeII_flows: pd.DataFrame) \
        -> pd.Series:
    """
    This function assign alternatives to the category which has the closet
    profile.

    :param categories: Indices of categories
    :param prometheeII_flows: DataFrame with Promethee II flows (positive,
    negative and net)

    :return: Series of assignments
    """
    global profiles_flows, alternative_flows

    alternative_assignments = {}
    for Ralternative, alternative_group_flows in prometheeII_flows.groupby(
            level=0):
        alternative = Ralternative[1:]
        profiles_flows = alternative_group_flows.iloc[:-1]
        alternative_flows = alternative_group_flows.iloc[-1]
        category_pos = np.argmin(np.abs(
            profiles_flows['net'].values -
            alternative_flows['net']))
        alternative_assignments[alternative] = categories[category_pos]
    return pd.Series(alternative_assignments)
