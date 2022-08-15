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
    Promethee I flows.
    """

    def __init__(self,
                 alternatives: List[str],
                 categories: List[str],
                 category_profiles: List[str],
                 profiles_performances: List[List[NumericValue]],
                 criteria: Tuple[List[NumericValue], List[NumericValue]],
                 negative_flows: Tuple[List[NumericValue], List[NumericValue]],
                 positive_flows: Tuple[List[NumericValue], List[NumericValue]],
                 comparison_with_profiles: CompareProfiles):
        """
        :param alternatives: List of alternatives names (strings only)
        :param categories: List of categories names (strings only)
        :param category_profiles: List of central, limiting or boundary profiles names which divide alternatives
        to proper categories (strings only)
        :param profiles_performances: 2D List of performances of each boundary profile in each criterion
        :param criteria: List of scales of each criterion and List of preference direction (0 for 'min' and 1 for 'max')
        :param negative_flows: List of negative flows of each alternative
        and List of negative flows of each boundary profile
        :param positive_flows: List of positive flows of each alternative
        and List of positive flows of each boundary profile
        :param comparison_with_profiles: Enum CompareProfiles - indicate information of profiles types used
        in calculation.
        """
        self.alternatives = alternatives
        self.categories = categories
        self.category_profiles = category_profiles
        self.profiles_performances = directed_alternatives_performances(profiles_performances, criteria[1])
        self.criteria = criteria
        self.negative_flows = negative_flows
        self.positive_flows = positive_flows
        self.comparison_with_profiles = comparison_with_profiles

    @staticmethod
    def append_to_classification(classification: Dict, positive_flow_class: str,
                                 negative_flow_class: str, positive_flow_class_id: int, negative_flow_class_id: int,
                                 alternative_name: str):

        if positive_flow_class != negative_flow_class:
            if positive_flow_class_id > negative_flow_class_id:
                classification[alternative_name].append([negative_flow_class, positive_flow_class])
            else:
                classification[alternative_name].append([positive_flow_class, negative_flow_class])
        else:
            classification[alternative_name].append([positive_flow_class])

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
        classification = {alternatives: [] for alternatives in self.alternatives}
        positive_flow_class = ""
        negative_flow_class = ""
        positive_flow_class_id = -1
        negative_flow_class_id = -1
        for alternative_name, alternative_positive_flow, alternative_negative_flow in zip(
                self.alternatives, self.positive_flows[0], self.negative_flows[0]):
            for i, profile_i in enumerate(self.profiles_performances[:-1]):
                if positive_flow_class == "":
                    if self.positive_flows[1][i] < alternative_positive_flow <= self.positive_flows[1][i + 1]:
                        positive_flow_class = self.categories[i]
                        positive_flow_class_id = i
                if negative_flow_class == "":
                    if self.negative_flows[1][i] >= alternative_negative_flow > self.negative_flows[1][i + 1]:
                        negative_flow_class = self.categories[i]
                        negative_flow_class_id = i
                if positive_flow_class != "" and negative_flow_class != "":
                    FlowSortI.append_to_classification(classification, positive_flow_class, negative_flow_class,
                                                       positive_flow_class_id, negative_flow_class_id, alternative_name)
                    break
        return classification

    def __boundary_profiles_sorting(self) -> Dict[str][List[str]]:
        """
        Comparing positive and negative flows of each alternative with all boundary profiles and assign them to
        correctly class.

        :return: Dictionary with alternatives classification
        """
        classification = {alternatives: [] for alternatives in self.alternatives}
        positive_flow_class = ""
        negative_flow_class = ""
        positive_flow_class_id = -1
        negative_flow_class_id = -1
        for alternative_name, alternative_positive_flow, alternative_negative_flow in zip(
                self.alternatives, self.positive_flows[0], self.negative_flows[0]):
            for i, profile_i in enumerate(self.profiles_performances):
                if positive_flow_class == "":
                    if i == 0:
                        if alternative_positive_flow <= self.positive_flows[1][i]:
                            positive_flow_class = self.categories[i]
                            positive_flow_class_id = i
                    elif i == len(self.category_profiles) - 1:
                        if alternative_positive_flow > self.positive_flows[1][i - 1]:
                            positive_flow_class = self.categories[i]
                            positive_flow_class_id = i
                    else:
                        if self.positive_flows[1][i - 1] < alternative_positive_flow <= self.positive_flows[1][i]:
                            positive_flow_class = self.categories[i]
                            positive_flow_class_id = i
                if negative_flow_class == "":
                    if i == 0:
                        if alternative_negative_flow > self.negative_flows[1][i]:
                            negative_flow_class = self.categories[i]
                            negative_flow_class_id = i
                    elif i == len(self.category_profiles) - 1:
                        if alternative_negative_flow <= self.negative_flows[1][i - 1]:
                            negative_flow_class = self.categories[i]
                            negative_flow_class_id = i
                    else:
                        if self.negative_flows[1][i - 1] >= alternative_negative_flow > self.negative_flows[1][i]:
                            negative_flow_class = self.categories[i]
                            negative_flow_class_id = i
                if positive_flow_class != "" and negative_flow_class != "":
                    FlowSortI.append_to_classification(classification, positive_flow_class, negative_flow_class,
                                                       positive_flow_class_id, negative_flow_class_id, alternative_name)
                    break
        return classification

    def __central_profiles_sorting(self) -> Dict[str][List[str]]:
        """
        Comparing positive and negative flows of each alternative with all central profiles and assign them to
        correctly class.

        :return: Dictionary with alternatives classification
        """
        classification = {alternatives: [] for alternatives in self.alternatives}
        positive_flow_class = ""
        negative_flow_class = ""
        positive_flow_class_id = -1
        negative_flow_class_id = -1
        for alternative_name, alternative_positive_flow, alternative_negative_flow in zip(
                self.alternatives, self.positive_flows[0], self.negative_flows[0]):
            for i, profile_i in enumerate(self.profiles_performances):
                if positive_flow_class == "":
                    if i == 0:
                        if alternative_positive_flow <= (self.positive_flows[1][i] + self.positive_flows[1][i + 1]) / 2:
                            positive_flow_class = self.categories[i]
                            positive_flow_class_id = i
                    elif i == len(self.category_profiles) - 1:
                        if (self.positive_flows[1][i - 1] + self.positive_flows[1][i]) / 2 < alternative_positive_flow:
                            positive_flow_class = self.categories[i]
                            positive_flow_class_id = i
                    else:
                        if (self.positive_flows[1][i - 1] + self.positive_flows[1][i]) / 2 < alternative_positive_flow \
                                <= (self.positive_flows[1][i] + self.positive_flows[1][i + 1]) / 2:
                            positive_flow_class = self.categories[i]
                            positive_flow_class_id = i
                if negative_flow_class == "":
                    if i == 0:
                        if alternative_negative_flow > (self.negative_flows[1][i] + self.negative_flows[1][i + 1]) / 2:
                            negative_flow_class = self.categories[i]
                            negative_flow_class_id = i
                    elif i == len(self.category_profiles) - 1:
                        if (self.negative_flows[1][i - 1] + self.negative_flows[1][i]) / 2 >= alternative_negative_flow:
                            negative_flow_class = self.categories[i]
                            negative_flow_class_id = i
                    else:
                        if (self.negative_flows[1][i - 1] + self.negative_flows[1][i]) / 2 \
                                >= alternative_negative_flow \
                                > (self.negative_flows[1][i] + self.negative_flows[1][i + 1]) / 2:
                            negative_flow_class = self.categories[i]
                            negative_flow_class_id = i
                if positive_flow_class != "" and negative_flow_class != "":
                    FlowSortI.append_to_classification(classification, positive_flow_class, negative_flow_class,
                                                       positive_flow_class_id, negative_flow_class_id, alternative_name)
                    break
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
