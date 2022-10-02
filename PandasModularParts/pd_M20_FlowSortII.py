import pandas as pd
from typing import List
from core.enums import CompareProfiles
from core.aliases import PerformanceTable, CriteriaFeatures
from core.sorting import pandas_check_dominance_condition


class FlowSortII:
    """
    This module computes the assignments of given alternatives to categories using FlowSort procedure based on
    Promethee II flows.
    """

    def __init__(self,
                 categories: List[str],
                 category_profiles: PerformanceTable,
                 criteria: CriteriaFeatures,
                 alternatives_flows: pd.Series,
                 category_profiles_flows: pd.Series,
                 comparison_with_profiles: CompareProfiles):
        """
        :param categories: List of categories names (strings only)
        :param category_profiles: DataFrame with category profiles performances
        :param criteria: Criteria features with preference direction of each criterion
        :param alternatives_flows: Series with alternatives names as index and net flows as values
        :param category_profiles_flows: Series with categories names as index and net flows as values
        :param comparison_with_profiles: Enum CompareProfiles - indicate information of profiles types used
        in calculation.
        """

        self.categories = categories
        self.category_profiles = category_profiles
        self.criteria = criteria
        self.alternatives_flows = alternatives_flows
        self.category_profiles_flows = category_profiles_flows
        self.comparison_with_profiles = comparison_with_profiles
        pandas_check_dominance_condition(self.criteria, self.category_profiles)

    def __limiting_profiles_sorting(self) -> pd.Series:
        """
        Comparing positive and negative flows of each alternative with all limiting profiles and assign them to
        correctly class.

        :return: Series with alternatives classification
        """
        classification = pd.Series(['None' for _ in self.alternatives_flows.index], index=self.alternatives_flows.index)

        for alternative, alternative_net_flow in self.alternatives_flows.items():
            for i, category, category_net_flow in enumerate(list(self.category_profiles_flows.items())[:-1]):
                if category_net_flow < alternative_net_flow <= self.category_profiles[i+1]:
                    classification[alternative] = self.categories[i]
        return classification

    def __boundary_profiles_sorting(self) -> pd.Series:
        """
        Comparing positive and negative flows of each alternative with all boundary profiles and assign them to
        correctly class.

        :return: Series with alternatives classification
        """
        classification = pd.Series(['None' for _ in self.alternatives_flows.index], index=self.alternatives_flows.index)

        for alternative, alternative_net_flow in self.alternatives_flows.items():
            for i, category, category_net_flow in enumerate(self.category_profiles_flows.items()):
                if i == 0:
                    if alternative_net_flow <= category_net_flow:
                        classification[alternative] = self.categories[i]
                        break
                elif i == self.category_profiles.shape[0] - 1:
                    if self.category_profiles_flows[i-1] < alternative_net_flow:
                        classification[alternative] = self.categories[i]
                else:
                    if self.category_profiles_flows[i-1] < alternative_net_flow <= category_net_flow:
                        classification[alternative] = self.categories[i]
                        break
        return classification

    def __central_profiles_sorting(self) -> pd.Series:
        """
        Comparing positive and negative flows of each alternative with all central profiles and assign them to
        correctly class.

        :return: Series with alternatives classification
        """
        classification = pd.Series(['None' for _ in self.alternatives_flows.index], index=self.alternatives_flows.index)

        for alternative, alternative_net_flow in self.alternatives_flows.items():
            for i, category, category_net_flow in enumerate(self.category_profiles_flows.items()):
                if i == 0:
                    if alternative_net_flow <= (category_net_flow + self.category_profiles_flows[i+1]) / 2:
                        classification[alternative] = self.categories[i]
                        break
                elif i == self.category_profiles.shape[0] - 1:
                    if (self.category_profiles_flows[i-1] + category_net_flow) / 2 < alternative_net_flow:
                        classification[alternative] = self.categories[i]
                else:
                    if (self.category_profiles_flows[i-1] + category_net_flow) / 2 < alternative_net_flow \
                            <= (category_net_flow + self.category_profiles_flows[i+1]) / 2:
                        classification[alternative] = self.categories[i]
                        break
        return classification

    def calculate_sorted_alternatives(self) -> pd.Series:
        """
        Sort alternatives to proper categories.

        :return: Dictionary with alternatives assigned to proper classes
        """
        if self.comparison_with_profiles == CompareProfiles.LIMITING_PROFILES:
            return self.__limiting_profiles_sorting()
        elif self.comparison_with_profiles == CompareProfiles.BOUNDARY_PROFILES:
            return self.__boundary_profiles_sorting()
        else:
            return self.__central_profiles_sorting()
