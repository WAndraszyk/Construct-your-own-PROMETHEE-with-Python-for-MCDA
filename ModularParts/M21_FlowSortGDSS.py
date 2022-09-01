from core.aliases import NumericValue
from typing import List, Tuple, Dict
from enum import Enum
from core.preference_commons import directed_alternatives_performances
import numpy as np


class CompareProfiles(Enum):
    """Enumeration of the compare profiles types."""

    CENTRAL_PROFILES = 1
    BOUNDARY_PROFILES = 2


class FlowSortGDSS:
    """
    This module computes the assignments of given alternatives to categories using FlowSort GDSS procedure.
    """

    def __init__(self, alternatives: List[str],  # string
                 categories: List[str],  # list of string
                 category_profiles: List[str],  # list of string (at least 2)
                 criteria: List[NumericValue],  # list of directions
                 alternative_global_net_flows: List[NumericValue],  # M21x
                 category_profiles_global_net_flows: List[List[List[NumericValue]]],  # M21x
                 profiles_performances: List[List[List[NumericValue]]],  # at least 2
                 weights_DMs: List[NumericValue],  # at least 2
                 comparison_with_profiles: CompareProfiles,
                 assign_to_better_class: bool = True
                 ):
        """
        :param alternatives: List of alternatives names (strings only)
        :param categories: List of categories names (strings only)
        :param category_profiles: List of central or boundary profiles names which divide alternatives
        to proper categories (strings only)
        :param criteria: List of scales of each criterion and List of preference direction (0 for 'min' and 1 for 'max')
        :param alternative_global_net_flows: List of global net flow for each alternative (module M21x)
        :param category_profiles_global_net_flows: 3D List of global net flow for each
        alternative, DM and category profile
        :param profiles_performances: 2D List of performances of each boundary profile in each criterion
        :param weights_DMs: List of weight of each DM
        :param comparison_with_profiles: Enum CompareProfiles - indicate information of profiles types used
        in calculation.
        :param assign_to_better_class: Boolean which describe preference of the DMs in final alternative assignment when
        distances to worse and better class are equal.
        """
        self.alternatives = alternatives
        self.categories = categories
        self.category_profiles = category_profiles
        self.criteria = criteria
        self.alternative_global_net_flows = alternative_global_net_flows
        self.category_profiles_global_net_flows = category_profiles_global_net_flows
        self.profiles_performances = [directed_alternatives_performances(single_DM_profiles_performances, criteria)
                                      for single_DM_profiles_performances in profiles_performances]
        self.weights_DMs = weights_DMs
        self.comparison_with_profiles = comparison_with_profiles
        self.assign_to_better_class = assign_to_better_class

        self.__check_dominance_condition()

    def __check_dominance_condition(self):
        """
        Check if each boundary profile is strictly worse in each criterion than betters profiles (even from other DM's)

        :raise ValueError: if any profile is not strictly worse in any criterion than any better profile
        """
        for criteria_i, _ in enumerate(self.criteria):
            for DM_i, DM_i_profiles_performances in enumerate(self.profiles_performances):
                for i, profile_i in enumerate(DM_i_profiles_performances[:-1]):
                    for DM_j, DM_j_profiles_performances in enumerate(self.profiles_performances):
                        profile_j = DM_j_profiles_performances[i + 1]
                        if profile_i[criteria_i] >= profile_j[criteria_i]:
                            raise ValueError("Each profile needs to be preferred over profiles which are worse than it,"
                                             " even they are from different DMs")

    def __classify_alternative(self, classification: Dict[str, List[str]],
                               not_classified: List[Tuple[str, Tuple[str, str],
                                                          List[NumericValue], List[NumericValue]]],
                               alternative_assignments: List[str], alternative_name: str
                               ) -> Tuple[Dict[str, List[str]], List[Tuple[str, Tuple[str, str],
                                                                           List[NumericValue], List[NumericValue]]]]:
        """
        Classify (or no) alternative to proper category. Used in first step of assignment.

        :param classification: Dictionary with categories and already classified alternatives
        :param not_classified: List of Tuples with all necessary data
        (alternative name, Tuple with worse and better category, List with DM indices which vote for worse category
        and List with DM indices which vote for better category) to assign those alternatives to single class
         in final step of assignment.
        :param alternative_assignments: List of categories to which DMs assigned this alternative
        :param alternative_name: Name of alternative to assign

        :return: Tuple with updated classification Dictionary and not_classified List
        """
        if len(set(alternative_assignments)) > 1:
            assignments_category_indices = sorted(
                [self.categories.index(category) for category in set(alternative_assignments)])
            worse_category = self.categories[assignments_category_indices[0]]
            better_category = self.categories[assignments_category_indices[1]]

            DMs_chose_worse_category = [i for i, category in enumerate(alternative_assignments) if
                                        category == worse_category]
            DMs_chose_better_category = [i for i, category in enumerate(alternative_assignments) if
                                         category == better_category]
            not_classified.append((alternative_name, (worse_category, better_category), DMs_chose_worse_category,
                                   DMs_chose_better_category))
        else:
            classification[alternative_assignments[0]].append(alternative_name)

        return classification, not_classified

    def __calculate_first_step_assignments(self) -> Tuple[Dict[str, List[str]], List[Tuple[str, Tuple[str, str],
                                                                                           List[NumericValue], List[
                                                                                               NumericValue]]]]:
        """
        Use first step of assignment of FlowSort GDSS method to classify alternatives.
        Calculate assignment of each DM for each alternative. If alternative assignment is not unanimous adds this
        alternative to not_classified list.

        :return: Tuple with classification Dictionary and not_classified List of Tuples of alternative name, Tuple with
         worse and better category, List with DM indices which vote for worse category and List with DM indices
         which vote for better category.
        """

        classification = {category: [] for category in self.categories}
        not_classified = []

        for alternative_name, alternative_global_net_flow, alternative_profile_global_net_flows in zip(
                self.alternatives, self.alternative_global_net_flows, self.category_profiles_global_net_flows):
            alternative_assignments = []
            for DM_i, alternative_profile_DM_global_net_flows in enumerate(alternative_profile_global_net_flows):
                if self.comparison_with_profiles == CompareProfiles.BOUNDARY_PROFILES:
                    for profile_category_i, profile_net_flow in enumerate(alternative_profile_DM_global_net_flows):
                        if profile_category_i == 0 and alternative_global_net_flow <= profile_net_flow:
                            alternative_assignments.append(self.categories[0])
                            break
                        elif profile_category_i == len(
                                self.category_profiles) - 1 and alternative_global_net_flow > profile_net_flow:
                            alternative_assignments.append(self.categories[-1])
                            break
                        elif alternative_global_net_flow <= profile_net_flow:
                            alternative_assignments.append(self.categories[profile_category_i])
                            break
                else:
                    profile_distances = [abs(profile_net_flow - alternative_global_net_flow) for profile_net_flow in
                                         alternative_profile_DM_global_net_flows]
                    category_index = np.argmin(profile_distances)
                    alternative_assignments.append(self.categories[category_index])

            classification, not_classified = self.__classify_alternative(classification, not_classified,
                                                                         alternative_assignments, alternative_name)

        return classification, not_classified

    def __calculate_final_assignments(self, classification: Dict[str, List[str]],
                                      not_classified: List[Tuple[str, Tuple[str, str], List[NumericValue],
                                                                 List[NumericValue]]]) -> Dict[str, List[str]]:
        """
        Use final step of assignment to classify alternatives which could not be classified in first step of assignment.
        Calculates distance to worse and better category based on DM's decision and DM's alternative profile net flows.
        Then classifies alternative to category which has smaller distance to it. If distances are the same,
         alternative is classified by using class param 'assign_to_better_class'.

        :param classification: Dictionary with categories and already classified alternatives
        :param not_classified: List of Tuples with all necessary data
        (alternative name, Tuple with worse and better category, List with DM indices which vote for worse category
        and List with DM indices which vote for better category) to assign those alternatives to single class
         in final step of assignment.

        :return: classification Dictionary with final classification.
        """
        final_classification = classification.copy()

        for alternative_name, (worse_category, better_category), \
            DMs_chose_worse_category, DMs_chose_better_category in not_classified:

            alternative_index = self.alternatives.index(alternative_name)
            worse_category_index = self.categories.index(worse_category)
            better_category_index = self.categories.index(better_category)

            if self.comparison_with_profiles == CompareProfiles.BOUNDARY_PROFILES:
                worse_distance = sum([DM_weight *
                                      (self.alternative_global_net_flows[alternative_index] -
                                       self.category_profiles_global_net_flows[alternative_index][DM_index][
                                           worse_category_index])
                                      for DM_weight, DM_index in zip(self.weights_DMs, DMs_chose_worse_category)])
                better_distance = sum([DM_weight *
                                       (self.category_profiles_global_net_flows[alternative_index][DM_index][
                                            better_category_index] -
                                        self.alternative_global_net_flows[alternative_index])
                                       for DM_weight, DM_index in zip(self.weights_DMs, DMs_chose_better_category)])
            else:
                worse_distance = sum([DM_weight *
                                      abs(self.category_profiles_global_net_flows[alternative_index][DM_index][
                                              worse_category_index] -
                                          self.alternative_global_net_flows[alternative_index])
                                      for DM_weight, DM_index in zip(self.weights_DMs, DMs_chose_worse_category)])
                better_distance = sum([DM_weight *
                                       abs(self.category_profiles_global_net_flows[alternative_index][DM_index][
                                               better_category_index] -
                                           self.alternative_global_net_flows[alternative_index])
                                       for DM_weight, DM_index in zip(self.weights_DMs, DMs_chose_better_category)])

            if better_distance > worse_distance:
                final_classification[worse_category].append(alternative_name)
            elif better_distance < worse_distance:
                final_classification[better_category].append(alternative_name)
            else:
                if self.assign_to_better_class:
                    final_classification[better_category].append(alternative_name)
                else:
                    final_classification[worse_category].append(alternative_name)

        return final_classification

    def calculate_sorted_alternatives(self) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
        """
        Sort alternatives to proper categories.

        :return: Dictionary with first step assignment classification
        and Dictionary with final step assignment classification.
        """
        first_step_assignments, not_classified = self.__calculate_first_step_assignments()
        final_step_assignments = self.__calculate_final_assignments(first_step_assignments, not_classified)

        first_step_full_assignments = first_step_assignments
        for alternative_name, (worse_category, better_category), _, _ in not_classified:
            first_step_full_assignments[worse_category].append(alternative_name)
            first_step_full_assignments[better_category].append(alternative_name)

        return first_step_full_assignments, final_step_assignments
