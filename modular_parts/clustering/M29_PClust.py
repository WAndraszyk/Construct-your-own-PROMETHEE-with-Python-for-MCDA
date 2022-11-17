import math

import pandas as pd
import random
import core.preference_commons as pc
from typing import List, Tuple, Dict
from modular_parts.flows import calculate_prometheeII_outranking_flows, calculate_net_outranking_flows
from modular_parts.preference import compute_preference_indices

__all__ = ['cluster_using_pclust']


def _initialize_the_central_profiles(alternatives_performances: pd.DataFrame,
                                     categories: pd.Index,
                                     directions: pd.Series) -> pd.DataFrame:
    """
    First step of clustering. Initialization of the central profiles. Profiles features have random values, but they
    keep the rule of not being worse than the worse profile.
    """
    min_and_max_performances = pd.DataFrame({'Min': alternatives_performances.min(),
                                             'Max': alternatives_performances.max()})

    central_profiles = pd.DataFrame(index=categories, dtype=float)
    for criterion, direction in zip(alternatives_performances.columns, directions):
        performances = []
        for _ in categories:
            value = random.uniform(min_and_max_performances.loc[criterion, 'Min'],
                                   min_and_max_performances.loc[criterion, 'Max'])
            while value in performances:
                value = random.uniform(min_and_max_performances.loc[criterion, 'Min'],
                                       min_and_max_performances.loc[criterion, 'Max'])
            performances.append(value)

        central_profiles[criterion] = sorted(performances, reverse=not direction)

    return central_profiles


def _calculate_prometheeII_flows(central_profiles_performances: pd.DataFrame,
                                 alternatives_performances: pd.DataFrame,
                                 preference_thresholds: pd.Series,
                                 indifference_thresholds: pd.Series,
                                 standard_deviations: pd.Series,
                                 generalized_criteria: pd.Series,
                                 directions: pd.Series,
                                 weights: pd.Series) -> pd.DataFrame:
    """
    Calculate the profiles net flows using this library module.
    """
    # print(central_profiles_performances)
    # print(alternatives_performances)

    alternatives_vs_profiles_preferences, _ = compute_preference_indices(alternatives_performances,
                                                                         preference_thresholds,
                                                                         indifference_thresholds,
                                                                         standard_deviations,
                                                                         generalized_criteria,
                                                                         directions,
                                                                         weights,
                                                                         central_profiles_performances)

    profiles_preferences, _ = compute_preference_indices(central_profiles_performances,
                                                         preference_thresholds,
                                                         indifference_thresholds,
                                                         standard_deviations,
                                                         generalized_criteria,
                                                         directions,
                                                         weights)


    prometheeII_flows = calculate_prometheeII_outranking_flows(alternatives_vs_profiles_preferences,
                                                               profiles_preferences)

    return prometheeII_flows


def _assign_the_alternatives_to_the_categories(prometheeII_flows: pd.DataFrame,
                                               categories: pd.Index,
                                               ) -> Tuple[Dict[str, List[str]],
                                                          Dict[str, Dict[str, List[str]]]]:
    """
    Second step of clustering. Assignment of the alternatives to the categories(principal or interval).

    :return: Tuple with dictionary with alternatives clustered to principal categories and dictionary with
    alternatives clustered to interval categories.
    """
    principal_categories = {category: [] for category in categories}
    interval_categories = {category: {subcategory: [] for subcategory in categories[i + 1:]}
                           for i, category in enumerate(categories)}

    for Ralternative, alternative_group_flows in prometheeII_flows.groupby(level=0):
        alternative = Ralternative[1:]

        alternative_flows = alternative_group_flows.iloc[-1]
        flows_differences = (alternative_group_flows.iloc[:-1] - alternative_flows).abs()

        positive_category = flows_differences['positive'].idxmin()
        negative_category = flows_differences['negative'].idxmin()

        if positive_category == negative_category:
            principal_categories[positive_category].append(alternative)
        elif categories.get_loc(positive_category) < categories.get_loc(negative_category):
            interval_categories[positive_category][negative_category].append(alternative)

    return principal_categories, interval_categories


def _update_of_the_central_profiles(principal_categories: Dict[str, List[str]],
                                    interval_categories: Dict[str, Dict[str, List[str]]],
                                    alternatives_performances: pd.DataFrame,
                                    central_profiles: pd.DataFrame,
                                    categories: pd.Index,
                                    directions: pd.Series) -> pd.DataFrame:
    """
    Third step of clustering. Update of the central profiles based on the alternatives assigned to the categories.

    :param principal_categories: Dictionary with principal categories as keys and clustered alternatives
     in list as values.
    """
    for i, category in enumerate(categories):
        if len(principal_categories[category]) > 0:
            central_profiles.loc[category] = \
                alternatives_performances.loc[principal_categories[category]].mean()
        else:
            if i == 0:
                alternatives_in_interval = 0
                new_profile_performances = pd.Series([0 for _ in alternatives_performances.columns],
                                                     index=alternatives_performances.columns)
                for subcategory, alternatives in interval_categories[category].items():
                    alternatives_in_interval += len(alternatives)
                    new_profile_performances += alternatives_performances.loc[alternatives].sum()

                if alternatives_in_interval > 0:
                    central_profiles.loc[category] = new_profile_performances / alternatives_in_interval
                else:
                    performances = []
                    for criterion, direction in zip(central_profiles.columns, directions):
                        if direction == 1:  # Maximization
                            min_range = alternatives_performances[criterion].min()
                            max_range = central_profiles.iloc[1, criterion]
                        else:  # Minimization
                            min_range = 0
                            max_range = central_profiles.iloc[1, criterion]
                        performances = [random.uniform(min_range, max_range) for _ in central_profiles.columns]

                    central_profiles.loc[category] = performances

            elif math.isclose(i, (len(categories) - 1)):
                performances = [random.uniform(central_profiles.iloc[i - 1, criterion],
                                               alternatives_performances[criterion].max())
                                for criterion in central_profiles.columns]
                central_profiles.loc[category] = performances
            else:
                performances = [random.uniform(central_profiles.iloc[i - 1, criterion],
                                               central_profiles.iloc[i + 1, criterion])
                                for criterion in central_profiles.columns]
                central_profiles.loc[category] = performances

    for criterion, direction in zip(central_profiles.columns, directions):
        central_profiles[criterion] = sorted(central_profiles[criterion], reverse=not direction)

    return central_profiles


def _calculate_homogenity_index(principal_categories: Dict[str, List[str]],
                                alternatives_preferences: pd.DataFrame,
                                categories: pd.Index) -> pd.Series:
    """
    Calculate the homogenity index in every cluster. It has to be minimized.

    :param principal_categories: Dictionary with principal categories as keys and clustered alternatives
     in list as values.

    :return: Series with homogenity index for every cluster.
    """
    homogenity_indices = pd.Series(index=categories)

    for category in categories:
        alternatives_in_category = principal_categories[category]
        if len(alternatives_in_category) > 0:
            homogenity_indices[category] = \
                alternatives_preferences.loc[alternatives_in_category, alternatives_in_category].sum().sum() \
                / (len(alternatives_in_category) ** 2 - len(alternatives_in_category))
        else:
            homogenity_indices[category] = 1

    return homogenity_indices


def _calculate_heterogenity_index(principal_categories: Dict[str, List[str]],
                                  alternatives_preferences: pd.DataFrame,
                                  categories: pd.Index) -> Dict[str, Dict[str, float]]:
    """
    Calculate the heterogenity index between each cluster. It has to be maximized.

    :param principal_categories: Dictionary with principal categories as keys and clustered alternatives
     in list as values.

    :return: Dictionary with the heterogenity index between each cluster (also interval clusters)
    """

    heterogenity_indices = {category: {subcategory: 0 for subcategory in categories[i + 1:]}
                            for i, category in enumerate(categories)[:-1]}

    for i, category in enumerate(categories[:-1]):
        alternatives_in_category = principal_categories[category]
        for subcategory in categories[i + 1:]:
            alternatives_in_subcategory = principal_categories[subcategory]
            if len(alternatives_in_category) > 0 and len(alternatives_in_subcategory) > 0:
                heterogenity_indices[category][subcategory] = \
                    alternatives_preferences.loc[
                        alternatives_in_category, alternatives_in_subcategory].values.mean() - \
                    alternatives_preferences.loc[
                        alternatives_in_subcategory, alternatives_in_category].values.mean()
            else:
                heterogenity_indices[category][subcategory] = 0

    return heterogenity_indices


def _calculate_global_quality_index(homogenity_indices: pd.Series,
                                    heterogenity_indices: Dict[str, Dict[str, float]],
                                    categories: pd.Index) -> float:
    """
    Calculate the global quality index. It has to be maximized.

    :param homogenity_indices: Series with the homogenity index in every cluster.
    :param heterogenity_indices: Dictionary with the heterogenity index between
    each cluster (also interval clusters).

    :return: Global quality index as float.
    """
    global_index = 0
    for i, category in enumerate(categories[:-1]):
        for subcategory in categories[i + 1:]:
            global_index += heterogenity_indices[category][subcategory]

    return global_index / homogenity_indices.sum()


def cluster_using_pclust(alternatives_performances: pd.DataFrame,
                         preference_thresholds: pd.Series,
                         indifference_thresholds: pd.Series,
                         standard_deviations: pd.Series,
                         generalized_criteria: pd.Series,
                         criteria_directions: pd.Series,
                         criteria_weights: pd.Series,
                         n_categories: int,
                         max_iterations: int = 100) -> Tuple[pd.Series, pd.DataFrame, float]:
    """
    Cluster the alternatives using PClust algorithm.

    :param alternatives_performances: DataFrame of alternatives' performances.
    :param preference_thresholds: Series of preference thresholds.
    :param indifference_thresholds: Series of indifference thresholds.
    :param standard_deviations: Series of standard deviations.
    :param generalized_criteria: Series of generalized criteria.
    :param criteria_directions: Series of directions.
    :param criteria_weights: Series of weights.
    :param n_categories: Number of categories
    :param max_iterations: Maximum number of iterations.

    :return: Tuple containing Series with the cluster labels, DataFrame with the central profiles
     and the global quality index as float.
    """
    categories = pd.Index([f'C{i}' for i in range(1, n_categories + 1)])
    alternatives_preferences, _ = compute_preference_indices(alternatives_performances,
                                                             preference_thresholds,
                                                             indifference_thresholds,
                                                             standard_deviations,
                                                             generalized_criteria,
                                                             criteria_directions,
                                                             criteria_weights)

    iteration = 0
    iteration_without_change = 0
    central_profiles_performances = _initialize_the_central_profiles(alternatives_performances, categories,
                                                                     criteria_directions)

    prometheeII_flows = _calculate_prometheeII_flows(central_profiles_performances, alternatives_performances,
                                                     preference_thresholds, indifference_thresholds,
                                                     standard_deviations, generalized_criteria,
                                                     criteria_directions, criteria_weights)

    principal_categories, interval_categories = _assign_the_alternatives_to_the_categories(prometheeII_flows,
                                                                                           categories)

    central_profiles = _update_of_the_central_profiles(principal_categories, interval_categories,
                                                       alternatives_performances, central_profiles_performances,
                                                       categories, criteria_directions)

    heterogenity_indices = prev_heterogenity_indices = _calculate_heterogenity_index(principal_categories,
                                                                                     alternatives_preferences,
                                                                                     categories)

    while iteration < max_iterations or iteration_without_change < 10:
        prometheeII_flows = _calculate_prometheeII_flows(central_profiles_performances, alternatives_performances,
                                                         preference_thresholds, indifference_thresholds,
                                                         standard_deviations, generalized_criteria,
                                                         criteria_directions, criteria_weights)

        principal_categories, interval_categories = _assign_the_alternatives_to_the_categories(prometheeII_flows,
                                                                                               categories)

        central_profiles = _update_of_the_central_profiles(principal_categories, interval_categories,
                                                           alternatives_performances, central_profiles_performances,
                                                           categories, criteria_directions)

        heterogenity_indices = _calculate_heterogenity_index(principal_categories,
                                                             alternatives_preferences,
                                                             categories)

        if heterogenity_indices == prev_heterogenity_indices:
            iteration_without_change += 1
        else:
            iteration_without_change = 0
            prev_heterogenity_indices = heterogenity_indices

    homogenity_indices = _calculate_homogenity_index(principal_categories, alternatives_preferences, categories)

    global_quality_index = _calculate_global_quality_index(homogenity_indices, heterogenity_indices, categories)

    assignments = pd.Series(index=alternatives_performances.index)
    for category, alternatives in principal_categories.items():
        for alternative in alternatives:
            assignments.loc[alternative] = category

    for category, subcategories in interval_categories.items():
        for subcategory, alternatives in subcategories.items():
            for alternative in alternatives:
                assignments.loc[alternative] = category + subcategory

    return assignments, central_profiles, global_quality_index
