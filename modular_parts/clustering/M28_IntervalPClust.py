"""
    This module contains the implementation of the interval clustering using
    modified P2Clust algorithm.

    Implementation and naming convention are taken from the
    :cite:p:'SarrazinaDeSmetRosenfeld2018'
"""

import pandas as pd
import random
from typing import List, Tuple, Dict

from core.input_validation import intervalp2clust_validation
from core.enums import FlowType, Direction
from core.clusters_commons import initialize_the_central_profiles
from modular_parts.flows import calculate_promethee_outranking_flows
from modular_parts.preference import compute_preference_indices

__all__ = ['cluster_using_interval_pclust']


def _calculate_profile_based_flows(central_profiles_performances: pd.DataFrame,
                                   alternatives_performances: pd.DataFrame,
                                   preference_thresholds: pd.Series,
                                   indifference_thresholds: pd.Series,
                                   standard_deviations: pd.Series,
                                   generalized_criteria: pd.Series,
                                   directions: pd.Series,
                                   weights: pd.Series
                                   ) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculate the profiles net flows using profile-based outranking flows
    method.

    :param: central_profiles_performances: pd.DataFrame with the profiles as
    index and criteria as columns. Contains the performances of
    the central profiles(centroids).
    :param: alternatives_performances: pd.DataFrame with the alternatives
    as index and criteria as columns. Contains the performances
    of the alternatives.
    :param: preference_thresholds: pd.Series with criteria as index and
    preference thresholds as values.
    :param: indifference_thresholds: pd.Series with criteria as index and
    indifference thresholds as values.
    :param: standard_deviations: pd.Series with criteria as index and
    standard deviations as values.
    :param: generalized_criteria: pd.Series with criteria as index and
    generalized criteria as values.
    :param: directions: pd.Series with criteria as index and directions as
    values.
    :param: weights: pd.Series with criteria as index and weights as values.
    :return: Tuple with pd.DataFrame with the MultiIndex("R" + alternatives,
     profiles + alternatives) as index and 'positive' and 'negative' columns
     and pd.DataFrame with the profiles as index and
     profiles as columns. First DataFrame contains the profiles-based flows
     of the profiles and the second DataFrame contains
     preferences between profiles.
    """

    # Use basic Promethee Preferences method to calculate the
    # "alternatives vs profiles" preferences
    alternatives_vs_profiles_preferences, _ = compute_preference_indices(
        alternatives_performances,
        preference_thresholds,
        indifference_thresholds,
        standard_deviations,
        generalized_criteria,
        directions,
        weights,
        central_profiles_performances)

    # Use basic Promethee Preferences method to calculate the profiles
    # preferences
    profiles_preferences, _ = compute_preference_indices(
        central_profiles_performances,
        preference_thresholds,
        indifference_thresholds,
        standard_deviations,
        generalized_criteria,
        directions,
        weights)

    # Use above calculated preferences to calculate the profiles-based flows
    profile_based_flows = calculate_promethee_outranking_flows(
        alternatives_vs_profiles_preferences,
        FlowType.PROFILE_BASED,
        profiles_preferences)

    return profile_based_flows, profiles_preferences


def _assign_the_alternatives_to_the_categories(
        profile_based_flows: pd.DataFrame,
        categories: pd.Index) -> Tuple[Dict[str, List[str]],
                                       Dict[str, Dict[str, List[str]]]]:
    """
    Second step of clustering. Assignment of the alternatives to the
    categories(principal or interval).

    :param: profile_based_flows: pd.DataFrame with the MultiIndex("R" +
    alternatives, profiles + alternatives) as index and 'positive' and
    'negative' columns. Contains the profiles-based flows.
    :param: categories: pd.Index with the principal categories names.
    :return: Tuple with dictionary with principal categories as keys and
    clustered alternatives in list as values and dictionary with principal
    categories as keys and dictionary with principal categories as keys and
    clustered alternatives in list as values. The submission of two categories
    in second Dictionary represents the interval category between them.
    """

    # Init dictionaries with assignments to principal or interval categories
    principal_categories = {category: [] for category in categories}
    interval_categories = \
        {category: {subcategory: [] for subcategory in categories[i + 1:]}
         for i, category in enumerate(categories)}

    # Iterate over alternatives "groups" in profile-based flows
    for Ralternative, alternative_group_flows in profile_based_flows.groupby(
            level=0):
        # Get the alternative name
        alternative = Ralternative[1:]
        # Extract alternative vs profiles flows
        alternative_flows = alternative_group_flows.iloc[-1]
        # Calculate distances from the alternative to the profiles
        flows_differences = (alternative_group_flows.iloc[
                             :-1] - alternative_flows).abs()

        # Find the closest profiles based on the positive and negative flows
        positive_category = flows_differences['positive'].idxmin()[1]
        negative_category = flows_differences['negative'].idxmin()[1]

        # Check if above categories are the same
        if positive_category == negative_category:
            # If yes, assign the alternative to the principal category
            principal_categories[positive_category].append(alternative)
        # else assign the alternative to the interval category
        elif categories.get_loc(positive_category) > categories.get_loc(
                negative_category):
            interval_categories[negative_category][positive_category].append(
                alternative)
        else:
            interval_categories[positive_category][negative_category].append(
                alternative)

    return principal_categories, interval_categories


def _update_of_the_central_profiles(
        principal_categories: Dict[str, List[str]],
        interval_categories: Dict[str, Dict[str, List[str]]],
        alternatives_performances: pd.DataFrame,
        central_profiles_preferences: pd.DataFrame,
        categories: pd.Index,
        directions: pd.Series) -> pd.DataFrame:
    """
    Update of the central profiles performances based on the
    alternatives assigned to the categories.

    :param: principal_categories: Dictionary with principal categories as keys
     and clustered alternatives in list as values. Contains the alternatives
     assigned to the principal categories.
    :param: interval_categories: Dictionary with categories as keys and
    dictionary with categories as keys and clustered
    alternatives in list as values. Contains the alternatives assigned to
    the interval categories.
    :param: alternatives_performances: pd.DataFrame with the alternatives as
    index and criteria as columns. Contains the performances of the
    alternatives.
    :param: central_profiles: pd.DataFrame with the profiles as index and
    criteria as columns. Contains the performances of the central profiles.
    :param: categories: pd.Index with the principal categories names.
    :param: directions: pd.Series with criteria as index and directions as
    values.
    :return: pd.DataFrame with the profiles as index and criteria as columns.
    Contains the updated performances of the central profiles(centroids).
    """

    # Iterate over categories
    for i, category in enumerate(categories):
        # Main case: if alternatives are assigned to the principal category
        # new profile is the centroid of the alternatives
        if len(principal_categories[category]) > 0:
            central_profiles_preferences.loc[category] = \
                alternatives_performances.loc[
                    principal_categories[category]].mean()
        # Edge case: if not a single alternatives are not assigned to the
        # principal category
        else:
            # For first and last category, new profile is the centroid of the
            # alternatives assigned to the interval category
            # If there are no alternatives assigned to the interval category,
            # new preferences are randomized from specific range
            if i == 0:
                # Count alternatives in interval categories and
                # sum their preferences
                alternatives_in_interval = 0
                new_profile_performances = pd.Series(
                    [0 for _ in alternatives_performances.columns],
                    index=alternatives_performances.columns)

                for subcategory, alternatives in \
                        interval_categories[category].items():
                    alternatives_in_interval += len(alternatives)
                    new_profile_performances += alternatives_performances.loc[
                        alternatives].sum()
                # If there are some alternatives in interval categories,
                # new profile preferences is the mean of the sum of
                # gathered alternatives preferences
                if alternatives_in_interval > 0:
                    central_profiles_preferences.loc[category] = \
                        new_profile_performances / alternatives_in_interval
                # If there are no alternatives in interval categories,
                # new profile performances are randomized from specific range
                else:
                    performances = []
                    for criterion, direction in \
                            zip(central_profiles_preferences.columns,
                                directions):
                        # If criterion is to be maximized, new profile
                        # performance is draw from range [0, the closest
                        # centroid performance]
                        if direction == Direction.MAX:  # Maximization
                            min_range = 0
                            max_range = central_profiles_preferences \
                                .iloc[1][criterion]
                        # If criterion is to be minimized, new profile
                        # performance is draw from range [the closest centroid
                        # performance, min of all alternatives performances]
                        else:  # Minimization
                            min_range = central_profiles_preferences \
                                .iloc[1][criterion]
                            max_range = alternatives_performances[
                                criterion].max()
                        performances.append(
                            random.uniform(min_range, max_range))

                    central_profiles_preferences.loc[category] = performances

            elif i == len(categories) - 1:
                # Count alternatives in interval categories and
                # sum their preferences
                alternatives_in_interval = 0
                new_profile_performances = pd.Series(
                    [0 for _ in alternatives_performances.columns],
                    index=alternatives_performances.columns)

                for subcategory, alternatives in \
                        interval_categories[category].items():
                    alternatives_in_interval += len(alternatives)
                    new_profile_performances += alternatives_performances.loc[
                        alternatives].sum()
                # If there are some alternatives in interval categories,
                # new profile preferences is the mean of the sum of
                # gathered alternatives preferences
                if alternatives_in_interval > 0:
                    central_profiles_preferences.loc[
                        category] = new_profile_performances \
                                    / alternatives_in_interval
                # If there are no alternatives in interval categories,
                # new profile performances are randomized from specific range
                else:
                    performances = []
                    for criterion, direction in \
                            zip(central_profiles_preferences.columns,
                                directions):
                        # If criterion is to be maximized, new profile
                        # performance is draw from range [the closest
                        # centroid performance, max of all alternatives]
                        if direction == Direction.MAX:  # Maximization
                            min_range = central_profiles_preferences \
                                .iloc[-2][criterion]
                            max_range = alternatives_performances[
                                criterion].max()
                        # If criterion is to be minimized, new profile
                        # performance is draw from range [min of all
                        # alternatives performances, the closest centroid
                        # performance]
                        else:  # Minimization
                            min_range = alternatives_performances[
                                criterion].min()
                            max_range = central_profiles_preferences \
                                .iloc[-2][criterion]
                        performances.append(
                            random.uniform(min_range, max_range))

                    central_profiles_preferences.loc[category] = performances
            # For other non-edge categories, new profile performances are
            # randomized from range between the closest centroids
            else:
                performances = []
                for criterion, direction in \
                        zip(central_profiles_preferences.columns, directions):
                    if direction == Direction.MAX:  # Maximization
                        min_range = central_profiles_preferences \
                            .iloc[i - 1][criterion]
                        max_range = central_profiles_preferences \
                            .iloc[i + 1][criterion]
                    else:  # Minimization
                        min_range = central_profiles_preferences \
                            .iloc[i + 1][criterion]
                        max_range = central_profiles_preferences \
                            .iloc[i - 1][criterion]
                    performances.append(random.uniform(min_range, max_range))

                central_profiles_preferences.loc[category] = performances

    # Sort criteria to avoid problems with dominance over weakest profiles
    for criterion, direction in \
            zip(central_profiles_preferences.columns, directions):
        reverse = (direction == Direction.MIN)
        central_profiles_preferences[criterion] = \
            sorted(central_profiles_preferences[criterion], reverse=reverse)

    return central_profiles_preferences


def _calculate_homogeneity_index(principal_categories: Dict[str, List[str]],
                                 alternatives_preferences: pd.DataFrame,
                                 categories: pd.Index) -> pd.Series:
    """
    Calculate the homogeneity index in every cluster. It has to be minimized.

    :param principal_categories: Dictionary with principal categories as keys
     and clustered alternatives in list as values. Contains the alternatives
     assigned to the principal categories
    :param alternatives_preferences: pd.Dataframe with alternatives as index
    and criteria as columns. Contains the alternatives preferences.
    :param categories: pd.Index with principal categories

    :return: pd.Series with categories as index and
    homogeneity indexes as values
    """
    homogeneity_indices = pd.Series(index=categories, dtype=float)

    for category in categories:
        alternatives_in_category = principal_categories[category]
        # Check if there are any alternatives in category
        if len(alternatives_in_category) > 1:
            # Sum up all preferences between alternatives in that cluster
            homogeneity_indices[category] = \
                alternatives_preferences.loc[alternatives_in_category,
                                             alternatives_in_category
                                             ].sum().sum() / \
                (len(alternatives_in_category) ** 2 - len(
                    alternatives_in_category))
        else:
            homogeneity_indices[category] = 1

    return homogeneity_indices


def _calculate_heterogeneity_index(central_profiles_preferences: pd.DataFrame,
                                   categories: pd.Index) -> pd.Series:
    """
    Calculate the heterogeneity index between each cluster. It has to be
    maximized.

    :param central_profiles_preferences: pd.Dataframe with profiles as index
    and criteria as columns. Contains the central profiles preferences.
    :param categories: pd.Index with principal categories
    :return: pd.Series with categories as index and heterogeneity indexes as
    values
    """
    heterogeneity_indices = pd.Series(dtype=float)
    for i, category in enumerate(categories[:-1]):
        # This index is calculated between two next centroids
        subcategory = categories[i + 1]
        heterogeneity_indices[category] = \
            central_profiles_preferences.loc[subcategory, category] - \
            central_profiles_preferences.loc[category, subcategory]

    return heterogeneity_indices


def _calculate_global_quality_index(homogeneity_indices: pd.Series,
                                    heterogeneity_indices: pd.Series
                                    ) -> float:
    """
    Calculate the global quality index. It has to be maximized.

    :param homogeneity_indices: pd.Series with categories as index and
    homogeneity indexes as values
    :param heterogeneity_indices: pd.Series with categories as index and
    heterogeneity indexes as values
    :return: float, global quality index
    """
    return heterogeneity_indices.sum() / homogeneity_indices.sum()


def cluster_using_interval_pclust(alternatives_performances: pd.DataFrame,
                                  preference_thresholds: pd.Series,
                                  indifference_thresholds: pd.Series,
                                  standard_deviations: pd.Series,
                                  generalized_criteria: pd.Series,
                                  criteria_directions: pd.Series,
                                  criteria_weights: pd.Series,
                                  n_categories: int,
                                  max_iterations: int = 100
                                  ) -> Tuple[pd.Series, pd.DataFrame, float]:
    """
    Cluster the alternatives using modified P2Clust algorithm. The idea of the
     algorithm is to classify the alternatives to central profiles and
     then update the central profiles(cluster) basing on the gathered
     alternatives. Procedure is repeated until distribution of alternatives
        to clusters is stable or number of max iterations is reached.
    To calculate preferences in this method basic Promethee Preference
    module is used

    :param alternatives_performances: pd.DataFrame with alternatives as index
    and criteria as columns
    :param preference_thresholds: pd.Series with criteria as index and
    preference thresholds as values
    :param indifference_thresholds: pd.Series with criteria as index and
    indifference thresholds as values
    :param standard_deviations: pd.Series with criteria as index and
    standard deviations as values
    :param generalized_criteria: pd.Series with criteria as index and
    GeneralCriterion Enums as values. Indicates preference function for
    computing preferences on this criterion
    :param criteria_directions: pd.Series with criteria as index and
    Direction Enums as values. Indicates if the criterion is maximized or
    minimized
    :param criteria_weights: pd.Series with criteria as index and criteria
    weights as values
    :param n_categories: integer, indicates number of clusters to create
    :param max_iterations: integer, sets maximum number of iterations.
    :return: Tuple with pd.Series with alternatives as index and cluster
    tag as values, pd.DataFrame with centroids tags as index and criteria
    as columns and global quality index as float. The pd.Series shows
    to which cluster the alternative belongs. The pd.DataFrame shows
    performances of central profiles(centroids).
    """

    # Input validation
    intervalp2clust_validation(alternatives_performances,
                               preference_thresholds,
                               indifference_thresholds,
                               standard_deviations, generalized_criteria,
                               criteria_directions, criteria_weights,
                               n_categories)

    # Create central profiles tags
    categories = pd.Index([f'C{i}' for i in range(1, n_categories + 1)])

    # Get aggregated preferences of alternatives
    alternatives_preferences, _ = compute_preference_indices(
        alternatives_performances,
        preference_thresholds,
        indifference_thresholds,
        standard_deviations,
        generalized_criteria,
        criteria_directions,
        criteria_weights)

    iteration = 0
    iteration_without_change = 0

    # Initialize central profiles performances
    central_profiles_performances = initialize_the_central_profiles(
        alternatives_performances, categories,
        criteria_directions)

    # Calculate flows between alternatives and central profiles
    profile_based_flows, central_profiles_preferences = \
        _calculate_profile_based_flows(
            central_profiles_performances,
            alternatives_performances,
            preference_thresholds,
            indifference_thresholds,
            standard_deviations,
            generalized_criteria,
            criteria_directions,
            criteria_weights)

    # Assign alternatives to principal categories or interval categories
    # using above flows
    principal_categories, interval_categories = \
        _assign_the_alternatives_to_the_categories(
            profile_based_flows,
            categories)

    # Update central profiles performances basing on
    # the classified alternatives
    central_profiles = _update_of_the_central_profiles(
        principal_categories,
        interval_categories,
        alternatives_performances,
        central_profiles_performances,
        categories,
        criteria_directions)

    # Save previous distribution of alternatives to clusters
    prev_principal_categories = principal_categories
    prev_interval_categories = interval_categories

    # Main loop of the algorithm: repeat until distribution of alternatives
    # to clusters is stable for 10 loops or number of max iterations
    # is reached
    while iteration < max_iterations and iteration_without_change < 10:

        # Calculate flows between alternatives and central profiles
        # (again, because profiles performances changed)
        profile_based_flows, central_profiles_preferences = \
            _calculate_profile_based_flows(
                central_profiles_performances,
                alternatives_performances,
                preference_thresholds,
                indifference_thresholds,
                standard_deviations,
                generalized_criteria,
                criteria_directions,
                criteria_weights)

        # Assign alternatives to principal categories or interval categories
        # using above flows
        principal_categories, interval_categories = \
            _assign_the_alternatives_to_the_categories(
                profile_based_flows,
                categories)

        # Update central profiles performances basing on
        # the classified alternatives
        central_profiles = _update_of_the_central_profiles(
            principal_categories, interval_categories,
            alternatives_performances, central_profiles_performances,
            categories, criteria_directions)

        # Check if distribution of alternatives to clusters is the same as
        # in previous iteration
        if prev_principal_categories == principal_categories and \
                prev_interval_categories == interval_categories:
            iteration_without_change += 1
        else:
            # Reset counter it distribution varies
            iteration_without_change = 0
            prev_principal_categories = principal_categories
            prev_interval_categories = interval_categories

        iteration += 1

    # Calculate global quality index (heterogeneity index and
    # homogeneity index are needed)

    # Calculate heterogeneity index between central profiles(centroids)
    heterogeneity_indices = _calculate_heterogeneity_index(
        central_profiles_preferences, categories)
    # Calculate homogeneity index between alternatives in each cluster
    homogeneity_indices = \
        _calculate_homogeneity_index(principal_categories,
                                     alternatives_preferences, categories)

    # Calculate global quality index
    global_quality_index = _calculate_global_quality_index(
        homogeneity_indices, heterogeneity_indices)

    # Prepare output
    # Insert principal categories assignments
    assignments = pd.Series(index=alternatives_performances.index, dtype=str)
    for category, alternatives in principal_categories.items():
        for alternative in alternatives:
            assignments.loc[alternative] = category
    # Insert interval categories assignments
    for category, subcategories in interval_categories.items():
        for subcategory, alternatives in subcategories.items():
            for alternative in alternatives:
                assignments.loc[alternative] = category + subcategory

    return assignments, central_profiles, global_quality_index
