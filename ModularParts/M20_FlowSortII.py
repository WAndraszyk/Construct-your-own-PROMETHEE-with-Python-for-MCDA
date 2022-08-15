from enum import Enum
from typing import List, Tuple, Dict

from core.aliases import NumericValue
from core.preference_commons import directed_alternatives_performances


class CompareProfiles(Enum):
    """Enumeration of the compare profiles types."""

    CENTRAL_PROFILES = 1
    BOUNDARY_PROFILES = 2
    LIMITING_PROFILES = 3


class FlowSortI:
    """
    This module computes the assignments of given alternatives to categories using FlowSort procedure based on
    Promethee II flows.
    """

    def __init__(self,
                 alternatives: List[str],
                 categories: List[str],
                 category_profiles: List[str],
                 profiles_performances: List[List[NumericValue]],
                 criteria: Tuple[List[NumericValue], List[NumericValue]],
                 flows: Tuple[List[NumericValue], List[NumericValue]],
                 comparison_with_profiles: CompareProfiles):
        """
        :param alternatives: List of alternatives names (strings only)
        :param categories: List of categories names (strings only)
        :param category_profiles: List of central, limiting or boundary profiles names which divide alternatives
        to proper categories (strings only)
        :param profiles_performances: 2D List of performances of each boundary profile in each criterion
        :param criteria: List of scales of each criterion and List of preference direction (0 for 'min' and 1 for 'max')
        :param flows: List of net flows of each alternative and List of net flows of each boundary profile
        :param comparison_with_profiles: Enum CompareProfiles - indicate information of profiles types used
        in calculation.
        """

        self.alternatives = alternatives
        self.categories = categories
        self.category_profiles = category_profiles
        self.profiles_performances = directed_alternatives_performances(profiles_performances, criteria[1])
        self.criteria = criteria
        self.flows = flows
        self.comparison_with_profiles = comparison_with_profiles

    def __check_dominance_condition(self):
        """
        Check if each boundary profile is strictly worse in each criterion than betters profiles

        :raise ValueError: if any profile is not strictly worse in any criterion than anny better profile
        """
        for criteria_i in range(len(self.criteria[0])):
            for i, profile_i in enumerate(self.profiles_performances):
                for j, profile_j in enumerate(self.profiles_performances[i:]):
                    if profile_j[criteria_i] < profile_i[criteria_i]:
                        raise ValueError("Profiles don't fulfill the dominance condition")

    def __limiting_profiles_sorting(self) -> Dict[str][List[str]]:
        """
        Comparing positive and negative flows of each alternative with all limiting profiles and assign them to
        correctly class.

        :return: Dictionary with alternatives classification
        """
        classification = {category: [] for category in self.categories}

        for alternative_name, alternative_net_flow in zip(self.alternatives, self.flows[0]):
            for i, profile_i in enumerate(self.profiles_performances[:-1]):
                if self.flows[1][i] < alternative_net_flow <= self.flows[1][i + 1]:
                    classification[self.categories[i]].append(alternative_name)
        return classification

    def __boundary_profiles_sorting(self) -> Dict[str][List[str]]:
        """
        Comparing positive and negative flows of each alternative with all boundary profiles and assign them to
        correctly class.

        :return: Dictionary with alternatives classification
        """
        classification = {category: [] for category in self.categories}

        for alternative_name, alternative_net_flow in zip(self.alternatives, self.flows[0]):
            for i, profile_i in enumerate(self.profiles_performances):
                if i == 0:
                    if alternative_net_flow <= self.flows[1][i]:
                        classification[self.categories[i]].append(alternative_name)
                elif i == len(self.category_profiles) - 1:
                    if self.flows[1][i - 1] < alternative_net_flow:
                        classification[self.categories[i]].append(alternative_name)
                else:
                    if self.flows[1][i - 1] < alternative_net_flow <= self.flows[1][i]:
                        classification[self.categories[i]].append(alternative_name)
        return classification

    def __central_profiles_sorting(self) -> Dict[str][List[str]]:
        """
        Comparing positive and negative flows of each alternative with all central profiles and assign them to
        correctly class.

        :return: Dictionary with alternatives classification
        """
        classification = {category: [] for category in self.categories}

        for alternative_name, alternative_net_flow in zip(self.alternatives, self.flows[0]):
            for i, profile_i in enumerate(self.profiles_performances):
                if i == 0:
                    if alternative_net_flow <= (self.flows[1][i] + self.flows[1][i + 1]) / 2:
                        classification[self.categories[i]].append(alternative_name)
                elif i == len(self.category_profiles) - 1:
                    if (self.flows[1][i - 1] + self.flows[1][i]) / 2 < alternative_net_flow:
                        classification[self.categories[i]].append(alternative_name)
                else:
                    if (self.flows[1][i - 1] + self.flows[1][i]) / 2 < alternative_net_flow \
                            <= (self.flows[1][i] + self.flows[1][i + 1]) / 2:
                        classification[self.categories[i]].append(alternative_name)
        return classification

    def calculate_sorted_alternatives(self) -> Dict[str][List[str]]:
        """
        Sort alternatives to proper categories.

        :return: Dictionary with alternatives assigned to proper classes
        """
        self.__check_dominance_condition()

        if self.comparison_with_profiles == CompareProfiles.LIMITING_PROFILES:
            return self.__limiting_profiles_sorting()
        elif self.comparison_with_profiles == CompareProfiles.BOUNDARY_PROFILES:
            return self.__boundary_profiles_sorting()
        else:
            return self.__central_profiles_sorting()
