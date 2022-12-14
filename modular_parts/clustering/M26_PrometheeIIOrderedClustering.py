"""
This module implements clustering method based on FlowSort and k-mean
algorithm.
"""
import numpy as np
import pandas as pd
import core.preference_commons as pc
from core.enums import FlowType
from core.clusters_commons import group_alternatives, \
    calculate_new_profiles, initialize_the_central_profiles
from core.input_validation import promethee_II_ordered_clustering_validation
from core.promethee_check_dominance import check_dominance_condition
from modular_parts.preference import compute_preference_indices
from modular_parts.flows import calculate_promethee_outranking_flows
from modular_parts.flows import calculate_net_outranking_flows

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
    :param n_categories: number of categories
    :param max_iterations: maximum number of iterations

    :return: Series with alternatives grouped into k ordered clusters
    """

    promethee_II_ordered_clustering_validation(alternatives_performances,
                                               preference_thresholds,
                                               indifference_thresholds,
                                               s_parameters,
                                               generalized_criteria,
                                               directions,
                                               weights,
                                               n_categories)

    # initialize central profiles
    categories = pd.Index([f'C{i}' for i in range(1, n_categories + 1)])
    central_profiles = initialize_the_central_profiles(
        alternatives_performances, categories, directions)

    # changing values of alternatives' performances according to direction
    # of criterion for further calculations
    alternatives_performances = pc.directed_alternatives_performances(
        alternatives_performances, directions)

    # sorting alternatives into categories
    assignments = _sort_alternatives_to_categories(alternatives_performances,
                                                   preference_thresholds,
                                                   indifference_thresholds,
                                                   s_parameters,
                                                   generalized_criteria,
                                                   directions, weights,
                                                   central_profiles,
                                                   categories)

    assignments_old = None
    iteration = 0

    # algorithm ends when assignment doesn't change anymore or loop iteration
    # reached max_iteration
    while (not assignments.equals(assignments_old)) and \
            iteration < max_iterations:
        iteration += 1
        assignments_old = assignments

        # update central profiles performance
        central_profiles = _calculate_new_profiles_mean(
            central_profiles, alternatives_performances, assignments)

        # sorting alternatives into categories
        assignments = _sort_alternatives_to_categories(
            alternatives_performances,
            preference_thresholds,
            indifference_thresholds,
            s_parameters,
            generalized_criteria,
            directions, weights,
            central_profiles,
            categories)

    # change output from Series with alternatives indices and categories
    # values to catego
    cluster = group_alternatives(assignments)
    cluster.sort_index(inplace=True)
    return cluster


def _sort_alternatives_to_categories(
        alternatives_performances: pd.DataFrame,
        preference_thresholds: pd.Series,
        indifference_thresholds: pd.Series, s_parameters: pd.Series,
        generalized_criteria: pd.Series,
        directions: pd.Series, weights: pd.Series,
        central_profiles: pd.DataFrame,
        categories: pd.Index) -> pd.Series:
    """
    This function calculates new partial preferences, Promethee II flows
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

    :return: Series with precise assignments of alternatives to categories

    """
    # calculating preference indices alternatives over profiles
    alternatives_preference, _ = compute_preference_indices(
        alternatives_performances, preference_thresholds,
        indifference_thresholds, s_parameters,
        generalized_criteria, directions, weights, central_profiles)

    # calculating preference indices profiles over profiles
    profiles_preference, _ = compute_preference_indices(
        central_profiles, preference_thresholds, indifference_thresholds,
        s_parameters, generalized_criteria, directions, weights)

    # calculating Net Outranking Flow
    prometheeII_flows = calculate_promethee_outranking_flows(
        alternatives_preference, FlowType.PROMETHEE_II,
        profiles_preference)
    prometheeII_flows = calculate_net_outranking_flows(prometheeII_flows,
                                                       True)

    redirected_profiles = pc.directed_alternatives_performances(
        central_profiles, directions)

    # Promethee II demands profiles to be dominated
    check_dominance_condition(directions, redirected_profiles)

    # sorting alternatives into categories
    assignments = calculate_flowsort_assignment(categories,
                                                prometheeII_flows)

    # if the category is empty, the algorithm force one alternative to
    # belonging to it
    assignments = _force_alternative_to_empty_category(assignments,
                                                       central_profiles.index)
    return assignments


def _calculate_new_profiles_mean(profiles_performances: pd.DataFrame,
                                 alternatives_performances: pd.DataFrame,
                                 assignment: pd.Series) -> pd.DataFrame:
    """
    This function updates profiles performances on the basis of the
    alternatives belonging to it using math mean function.

    :param profiles_performances: Dataframe of profiles performance (value)
        at every criterion, index: profiles, columns: criteria
    :param alternatives_performances: Dataframe of alternatives' value at
        every criterion, index: alternatives, columns: criteria
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


def _force_alternative_to_empty_category(assignments: pd.Series,
                                         categories: pd.Index) -> pd.Series:
    """
    In case given category disappear (is empty) during the execution of the
    algorithm, method force randomly chosen alternative to belong to the
    category.

    :param assignments: Series with precise assignments of alternatives to
        categories
    :param categories: Indices of categories

    :return: Redefined assignments without empty categories
    """
    assignments_copy = assignments.copy(deep=True)

    # the algorithm doesn't force alternatives to empty category if that
    # alternative is the only one belonging to its category
    old_value = []
    while True:
        item = assignments_copy.sample()
        unique_category = assignments_copy.unique()
        # categories which are not in unique categories are empty
        if list(set(categories.values) - set(unique_category)) == []:
            break

        # if the alternative's category is in old_value, that is its category
        #  got more assigned alternatives, alternative can be forced
        # this alternative to an empty category
        if item.values in old_value:
            assignments_copy[item.keys()] = np.random.choice(
                list(set(categories) - set(unique_category)))
        else:
            old_value += [np.random.choice(item.values)]
    return assignments_copy


def calculate_flowsort_assignment(categories: pd.Index,
                                  prometheeII_flows: pd.DataFrame) \
        -> pd.Series:
    """
    This function assign alternatives to the category which has the closet
    profile.

    :param categories: list of categories
    :param prometheeII_flows: DataFrame with Promethee II flows (positive,
    negative and net)

    :return: Series of assignments
    """

    alternative_assignments = {}

    # Iterate over flow groups (profiles + alternative)
    for Ralternative, alternative_group_flows in prometheeII_flows.groupby(
            level=0):
        # Get alternative name
        alternative = Ralternative[1:]

        # Separate profiles and alternative flows
        profiles_flows = alternative_group_flows.iloc[:-1]
        alternative_flows = alternative_group_flows.iloc[-1]

        # Assign alternative to category with the closest net flow
        category_pos = np.argmin(np.abs(
            profiles_flows['net'].values -
            alternative_flows['net']))
        alternative_assignments[alternative] = categories[category_pos]
    return pd.Series(alternative_assignments)
