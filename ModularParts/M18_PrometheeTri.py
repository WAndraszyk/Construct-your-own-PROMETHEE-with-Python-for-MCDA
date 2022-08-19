from core.aliases import NumericValue
from typing import List, Tuple, Dict


class PrometheeTri:
    """
    This module computes the assignments of given alternatives to categories using Promethee Tri method.
    """

    def __init__(self,
                 alternatives: List[str],
                 categories: List[str],
                 category_profiles: List[str],
                 criteria: List[str],
                 criteria_weights: List[NumericValue],
                 partial_preferences: Tuple[List[List[NumericValue]], List[List[NumericValue]]],
                 assign_to_better_class: bool = True,
                 use_marginal_value: bool = True):
        """
        :param alternatives: List of alternatives names (strings only)
        :param categories: List of categories names (strings only)
        :param category_profiles: List of boundary profiles names which divide alternatives
        to proper categories (strings only)
        :param criteria: List of criteria names (strings only)
        :param criteria_weights: List of weight of each criterion
        :param partial_preferences: 2D List of alternatives partial preferences and
        2D List of profiles partial preferences
        :param assign_to_better_class: Boolean which describe preference of the DM in final alternative assignment when
        deviation for two or more profiles are the same.
        :param use_marginal_value: Boolean which describe whether deviation should be
        calculated as absolute value or not
        """
        self.alternatives = alternatives
        self.categories = categories
        self.category_profiles = category_profiles
        self.criteria = criteria
        self.criteria_weights = criteria_weights
        self.partial_preferences = partial_preferences
        self.assign_to_better_class = assign_to_better_class
        self.use_marginal_value = use_marginal_value

    def __calculate_criteria_net_flows(self) -> Tuple[List[List[NumericValue]], List[List[NumericValue]]]:
        """
        Calculate criteria net flows for profiles and alternatives.

        :return: 2D List of criteria net flows for profiles and 2D List of criteria net flows for alternatives.
        """
        profiles_criteria_net_flows = []
        alternatives_criteria_net_flows = []

        n_profiles = len(self.category_profiles)
        for i, _ in enumerate(self.category_profiles):
            profile_criteria_net_flows = []
            for j, _ in enumerate(self.criteria):
                criterion_net_flow = 0
                for k, _ in enumerate(self.alternatives):
                    if i != k:
                        criterion_net_flow += self.partial_preferences[0][i][k] - self.partial_preferences[0][k][i]
                profile_criteria_net_flows.append(1 / (n_profiles - 1) * criterion_net_flow)
            profiles_criteria_net_flows.append(profile_criteria_net_flows)

        n_alternatives = len(self.alternatives)
        for i, _ in enumerate(self.alternatives):
            alternative_criteria_net_flows = []
            for j, _ in enumerate(self.criteria):
                criterion_net_flow = 0
                for k, _ in enumerate(self.alternatives):
                    if i != k:
                        criterion_net_flow += self.partial_preferences[0][i][k] - self.partial_preferences[0][k][i]
                alternative_criteria_net_flows.append(1 / n_alternatives * criterion_net_flow)
            alternatives_criteria_net_flows.append(alternative_criteria_net_flows)

        return profiles_criteria_net_flows, alternatives_criteria_net_flows

    def __calculate_deviations(self, profiles_criteria_net_flows: List[List[NumericValue]],
                               alternatives_criteria_net_flows: List[List[NumericValue]]) -> List[List[NumericValue]]:
        """
        Calculate deviation for each alternative and each profile.

        :param profiles_criteria_net_flows: 2D List of criteria net flows for profiles
        :param alternatives_criteria_net_flows: 2D List of criteria net flows for alternatives

        :return: 2D List of deviations
        """
        deviations = []

        for alternative_criteria_net_flows in alternatives_criteria_net_flows:
            alternative_deviations = []
            for profile_criteria_net_flows in profiles_criteria_net_flows:
                deviation = 0
                for i, criteria_weight in enumerate(self.criteria_weights):
                    if self.use_marginal_value:
                        deviation += abs(alternative_criteria_net_flows[i] - profile_criteria_net_flows[i])\
                                     * criteria_weight
                    else:
                        deviation += (alternative_criteria_net_flows[i] - profile_criteria_net_flows[i]) \
                                     * criteria_weight
                alternative_deviations.append(deviation)
            deviations.append(alternative_deviations)

        return deviations

    def __assign_alternatives_to_classes_with_minimal_deviation(self, deviations: List[List[NumericValue]]
                                                                ) -> Dict[str][str]:
        """
        Assign every alternative to class with minimal deviation for pair alternative, class.

        :param deviations: 2D List of deviations

        :return: Dictionary with alternatives assigned to proper classes
        """
        classification = {category: [] for category in self.categories}

        for alternative_index, alternative_deviations in enumerate(deviations):
            min_deviation_value = min(alternative_deviations)

            min_deviation_indices = [i for i, deviation in alternative_deviations if deviation == min_deviation_value]

            if len(min_deviation_indices) == 1 or self.assign_to_better_class:
                category_index = min_deviation_indices[0]
            else:
                category_index = min_deviation_indices[-1]

            classification[self.categories[category_index]].append(self.alternatives[alternative_index])

        return classification

    def calculate_sorted_alternatives(self):
        """
        Sort alternatives to proper categories.

        :return: Dictionary with alternatives assigned to proper classes
        """
        profiles_criteria_net_flows, alternatives_criteria_net_flows = self.__calculate_criteria_net_flows()
        deviations = self.__calculate_deviations(profiles_criteria_net_flows, alternatives_criteria_net_flows)
        return self.__assign_alternatives_to_classes_with_minimal_deviation(deviations)
