import pandas as pd
import random
import core.preference_commons as pc
from typing import List, Tuple, Dict
from ModularParts.flows.M9_PrometheeOutrankingFlows import PrometheeOutrankingFlows
from ModularParts.preference.M3_PrometheePreference import PrometheePreference


class PClust:

    def __init__(self, alternatives_performances: pd.DataFrame,
                 preference_thresholds: pd.Series,
                 indifference_thresholds: pd.Series,
                 standard_deviations: pd.Series,
                 generalized_criteria: pd.Series,
                 directions: pd.Series,
                 weights: pd.Series,
                 n_categories: int,
                 alternatives_flows: pd.DataFrame,
                 max_iterations: int = 100):
        """
        :param alternatives_performances: DataFrame of alternatives' performances.
        :param preference_thresholds: Series of preference thresholds.
        :param indifference_thresholds: Series of indifference thresholds.
        :param standard_deviations: Series of standard deviations.
        :param generalized_criteria: Series of generalized criteria.
        :param directions: Series of directions.
        :param weights: Series of weights.
        :param n_categories: Number of categories
        :param alternatives_flows: DataFrame with alternatives net flows (positive and negative )
        :param max_iterations: Maximum number of iterations.
        """
        self.alternatives_performances = pc.directed_alternatives_performances(alternatives_performances, directions)
        self.preference_thresholds = preference_thresholds
        self.indifference_thresholds = indifference_thresholds
        self.standard_deviations = standard_deviations
        self.generalized_criteria = generalized_criteria
        self.directions = directions
        self.weights = weights
        self.categories = pd.Index(['C{i}' for i in range(1, n_categories + 1)])
        self.alternatives_flows = alternatives_flows
        self.max_iterations = max_iterations

        preferences_module = PrometheePreference(self.alternatives_performances,
                                                 self.preference_thresholds,
                                                 self.indifference_thresholds,
                                                 self.standard_deviations,
                                                 self.generalized_criteria,
                                                 self.directions,
                                                 self.weights)
        self.alternatives_preferences, _ = preferences_module.computePreferenceIndices()

    def __initializate_of_the_central_profiles(self):
        """
        First step of clustering. Initialization of the central profiles. Profiles features have random values, but they
        keep the rule of not being worse than the worse profile.
        """
        min_and_max_performances = pd.DataFrame({'Min': self.alternatives_performances.min(),
                                                 'Max': self.alternatives_performances.max()})

        self.central_profiles = pd.DataFrame(index=self.categories)
        for criterion, direction in zip(self.alternatives_performances.columns, self.directions):
            performances = []
            for _ in self.categories:
                value = random.uniform(min_and_max_performances.loc[criterion, 'Min'],
                                       min_and_max_performances.loc[criterion, 'Max'])
                while value in performances:
                    value = random.uniform(min_and_max_performances.loc[criterion, 'Min'],
                                           min_and_max_performances.loc[criterion, 'Max'])
                performances.append(value)

            self.central_profiles[criterion] = sorted(performances, reverse=not direction)

    def __calculate_profiles_net_flows(self):
        """
        Calculate the profiles net flows using this library module.
        """
        preferences_module = PrometheePreference(self.central_profiles,
                                                 self.preference_thresholds,
                                                 self.indifference_thresholds,
                                                 self.standard_deviations,
                                                 self.generalized_criteria,
                                                 self.directions,
                                                 self.weights)

        profiles_preferences, _ = preferences_module.computePreferenceIndices()

        outranking_flows = PrometheeOutrankingFlows(preferences=profiles_preferences)
        self.profiles_flows = outranking_flows.calculate_flows()

    def __assign_of_the_alternatives_to_the_categories(self) -> Tuple[Dict[str, List[str]],
                                                                      Dict[str, Dict[str, List[str]]]]:
        """
        Second step of clustering. Assignment of the alternatives to the categories(principal or interval).

        :return: Tuple with dictionary with alternatives clustered to principal categories and dictionary with
        alternatives clustered to interval categories.
        """
        principal_categories = {category: [] for category in self.categories}
        interval_categories = {category: {subcategory: [] for subcategory in self.categories[i + 1:]}
                               for i, category in enumerate(self.categories)}

        for alternative, row in self.alternatives_performances.iterrows():
            positive_differences = (self.profiles_flows['positive'] - row['positive']).abs()
            negative_differences = (self.profiles_flows['negative'] - row['negative']).abs()

            positive_category = positive_differences.idxmin()
            negative_category = negative_differences.idxmin()

            if positive_category == negative_category:
                principal_categories[positive_category].append(alternative)
            elif self.categories.get_loc(positive_category) < self.categories.get_loc(negative_category):
                interval_categories[positive_category][negative_category].append(alternative)

        return principal_categories, interval_categories

    def __update_of_the_central_profiles(self, principal_categories: Dict[str, List[str]],
                                         interval_categories: Dict[str, Dict[str, List[str]]]):
        """
        Third step of clustering. Update of the central profiles based on the alternatives assigned to the categories.

        :param principal_categories: Dictionary with principal categories as keys and clustered alternatives
         in list as values.
        """
        for i, category in enumerate(self.categories):
            if len(principal_categories[category]) > 0:
                self.central_profiles.loc[category] = \
                    self.alternatives_performances.loc[principal_categories[category]].mean()
            else:
                if i == 0:
                    alternatives_in_interval = 0
                    new_profile_performances = pd.Series([0 for _ in self.alternatives_performances.columns],
                                                         index=self.alternatives_performances.columns)
                    for subcategory, alternatives in interval_categories[category].items():
                        alternatives_in_interval += len(alternatives)
                        new_profile_performances += self.alternatives_performances.loc[alternatives].sum()

                    if alternatives_in_interval > 0:
                        self.central_profiles.loc[category] = new_profile_performances / alternatives_in_interval
                    else:
                        performances = []
                        for criterion, direction in zip(self.central_profiles.columns, self.directions):
                            if direction == '1':  # Maximization
                                min_range = self.alternatives_performances[criterion].min()
                                max_range = self.central_profiles[1][criterion]
                            else:  # Minimization
                                min_range = 0
                                max_range = self.central_profiles[1][criterion]
                            performances = [random.uniform(min_range, max_range) for _ in self.central_profiles.columns]

                        self.central_profiles.loc[category] = performances

                elif i == len(self.categories) - 1:
                    performances = [random.uniform(self.central_profiles[i - 1][criterion],
                                                   self.alternatives_performances[criterion].max())
                                    for criterion in self.central_profiles.columns]
                    self.central_profiles.loc[category] = performances
                else:
                    performances = [random.uniform(self.central_profiles[i - 1][criterion],
                                                   self.central_profiles[i + 1][criterion])
                                    for criterion in self.central_profiles.columns]
                    self.central_profiles.loc[category] = performances

        for criterion, direction in zip(self.central_profiles.columns, self.directions):
            self.central_profiles[criterion] = sorted(self.central_profiles[criterion], reverse=not direction)

    def __calculate_homogenity_index(self, principal_categories: Dict[str, List[str]]) -> pd.Series:
        """
        Calculate the homogenity index in every cluster. It has to be minimized.

        :param principal_categories: Dictionary with principal categories as keys and clustered alternatives
         in list as values.

        :return: Series with homogenity index for every cluster.
        """
        homogenity_indices = pd.Series(index=self.categories)

        for category in self.categories:
            alternatives_in_category = principal_categories[category]
            if len(alternatives_in_category) > 0:
                homogenity_indices[category] = \
                    self.alternatives_preferences.loc[alternatives_in_category, alternatives_in_category] \
                        .sum().sum() / (len(alternatives_in_category) ** 2 - len(alternatives_in_category))
            else:
                homogenity_indices[category] = 1

        return homogenity_indices

    def __calculate_heterogenity_index(self, principal_categories: Dict[str, List[str]]) -> Dict[str, Dict[str, float]]:
        """
        Calculate the heterogenity index between each cluster. It has to be maximized.

        :param principal_categories: Dictionary with principal categories as keys and clustered alternatives
         in list as values.

        :return: Dictionary with the heterogenity index between each cluster (also interval clusters)
        """

        heterogenity_indices = {category: {subcategory: 0 for subcategory in self.categories[i + 1:]}
                                for i, category in enumerate(self.categories)[:-1]}

        for i, category in enumerate(self.categories[:-1]):
            alternatives_in_category = principal_categories[category]
            for subcategory in self.categories[i + 1:]:
                alternatives_in_subcategory = principal_categories[subcategory]
                if len(alternatives_in_category) > 0 and len(alternatives_in_subcategory) > 0:
                    heterogenity_indices[category][subcategory] = \
                        self.alternatives_preferences.loc[
                            alternatives_in_category, alternatives_in_subcategory].values.mean() - \
                        self.alternatives_preferences.loc[
                            alternatives_in_subcategory, alternatives_in_category].values.mean()
                else:
                    heterogenity_indices[category][subcategory] = 0

        return heterogenity_indices

    def __calculate_global_quality_index(self, homogenity_indices: pd.Series,
                                         heterogenity_indices: Dict[str, Dict[str, float]]) -> float:
        """
        Calculate the global quality index. It has to be maximized.

        :param homogenity_indices: Series with the homogenity index in every cluster.
        :param heterogenity_indices: Dictionary with the heterogenity index between
        each cluster (also interval clusters).

        :return: Global quality index as float.
        """
        global_index = 0
        for i, category in enumerate(self.categories[:-1]):
            for subcategory in self.categories[i + 1:]:
                global_index += heterogenity_indices[category][subcategory]

        return global_index / homogenity_indices.sum()

    def cluster(self) -> Tuple[pd.Series, pd.DataFrame, float]:
        """
        Cluster the alternatives using PClust algorithm.

        :return: Tuple containing Series with the cluster labels, DataFrame with the central profiles
         and the global quality index as float.
        """

        iteration = 0
        iteration_without_change = 0
        self.__initializate_of_the_central_profiles()
        self.__calculate_profiles_net_flows()

        principal_categories, interval_categories = self.__assign_of_the_alternatives_to_the_categories()
        self.__update_of_the_central_profiles(principal_categories, interval_categories)
        heterogenity_indices = prev_heterogenity_indices = self.__calculate_heterogenity_index(principal_categories)

        while iteration < self.max_iterations or iteration_without_change < 10:
            self.__calculate_profiles_net_flows()
            principal_categories, interval_categories = self.__assign_of_the_alternatives_to_the_categories()
            self.__update_of_the_central_profiles(principal_categories, interval_categories)
            heterogenity_indices = self.__calculate_heterogenity_index(principal_categories)

            if heterogenity_indices == prev_heterogenity_indices:
                iteration_without_change += 1
            else:
                iteration_without_change = 0
                prev_heterogenity_indices = heterogenity_indices

        homogenity_indices = self.__calculate_homogenity_index(principal_categories)

        global_quality_index = self.__calculate_global_quality_index(homogenity_indices, heterogenity_indices)

        assignments = pd.Series(index=self.alternatives_performances.index)
        for category, alternatives in principal_categories.items():
            for alternative in alternatives:
                assignments.loc[alternative] = category

        for category, subcategories in interval_categories.items():
            for subcategory, alternatives in subcategories.items():
                for alternative in alternatives:
                    assignments.loc[alternative] = category+subcategory

        return assignments, self.central_profiles, global_quality_index
