import numpy as np
import pandas as pd
import core.preference_commons as pc
from core.enums import CompareProfiles, FlowType
from core.clusters_commons import group_alternatives, \
    calculate_new_profiles, initialization_of_the_central_profiles
from core.input_validation import promethee_II_ordered_clustering_validation
from modular_parts.preference import compute_preference_indices
from modular_parts.sorting.M21_FlowSortII import \
    calculate_flowsortII_sorted_alternatives
from modular_parts.flows.M8_PrometheeOutrankingFlows import \
    calculate_promethee_outranking_flows
from modular_parts.flows.M9_NetOutrankingFlow import \
    calculate_net_outranking_flows_for_prometheeII

__all__ = ['promethee_II_ordered_clustering']


def promethee_II_ordered_clustering(alternatives_performances: pd.DataFrame,
                                    preference_thresholds: pd.Series,
                                    indifference_thresholds: pd.Series,
                                    standard_deviations: pd.Series,
                                    generalized_criteria: pd.Series,
                                    directions: pd.Series,
                                    weights: pd.Series,
                                    n_categories: int) -> pd.Series:
    """
    Cluster the alternatives using k-mean algorithm and PrometheeII.

    :param alternatives_performances: DataFrame of alternatives' performances.
    :param preference_thresholds: Series of preference thresholds.
    :param indifference_thresholds: Series of indifference thresholds.
    :param standard_deviations: Series of standard deviations.
    :param generalized_criteria: Series of generalized criteria.
    :param directions: Series of directions.
    :param weights: Series of weights.
    :param n_categories: Number of categories

    :return: Tuple containing Series with the cluster labels and grouped
    alternatives' data."""

    promethee_II_ordered_clustering_validation(alternatives_performances,
                                               preference_thresholds,
                                               indifference_thresholds,
                                               standard_deviations,
                                               generalized_criteria,
                                               directions,
                                               weights,
                                               n_categories)
    global sorted_old
    alternatives_performances = pc.directed_alternatives_performances(
        alternatives_performances, directions)
    categories = pd.Index([f'C{i}' for i in range(1, n_categories + 1)])

    def which_profile():
        return CompareProfiles.CENTRAL_PROFILES

    central_profiles = initialization_of_the_central_profiles(
        alternatives_performances, categories, directions)
    sorted = _sort_alternatives_to_categories(alternatives_performances,
                                              preference_thresholds,
                                              indifference_thresholds,
                                              standard_deviations,
                                              generalized_criteria,
                                              directions, weights,
                                              central_profiles, categories,
                                              which_profile)
    sorted_old = None
    while not sorted.equals(sorted_old):
        sorted_old = sorted
        central_profiles = _calculate_new_profiles_median(
            central_profiles, alternatives_performances, sorted)
        sorted = _sort_alternatives_to_categories(alternatives_performances,
                                                  preference_thresholds,
                                                  indifference_thresholds,
                                                  standard_deviations,
                                                  generalized_criteria,
                                                  directions, weights,
                                                  central_profiles,
                                                  categories, which_profile)

    cluster = group_alternatives(sorted)
    cluster.sort_index(inplace=True)
    return cluster


def _sort_alternatives_to_categories(
        alternatives_performances, preference_thresholds,
        indifference_thresholds, standard_deviations, generalized_criteria,
        directions, weights, central_profiles, categories, which_profile):
    """
    Calculates new partial preferences, prometheeII_flows, applies flowsortII
    and redefines new clusters.

    :return: Alternatives assignment

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
    sorted = calculate_flowsortII_sorted_alternatives(categories.tolist(),
                                                      redirected_profiles,
                                                      directions,
                                                      prometheeII_flows,
                                                      which_profile())[
        'negative']
    sorted = _force_alternative_to_empty_category(sorted,
                                                  central_profiles.index)

    return sorted


def _calculate_new_profiles_median(profiles, alternatives_performances,
                                   sorted):
    profiles = calculate_new_profiles(profiles, alternatives_performances,
                                      sorted, np.mean)
    profiles.fillna(0, inplace=True)
    profiles = profiles.apply(lambda x: x.sort_values().values)
    return profiles


def _force_alternative_to_empty_category(sorted: pd.Series,
                                         categories: pd.Index) -> pd.Series:
    """
    In case given category disappear (is empty) during the execution of the
     algorithm, method force randomly chosen
    alternative to belong to the category.

    :return: Redefined sorted without empty categories

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
            old_value += [item.values[0]]
    return sorted_copy
