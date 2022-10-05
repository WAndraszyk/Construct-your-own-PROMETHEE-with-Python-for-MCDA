import pandas as pd
from typing import List, Hashable
from core.enums import CompareProfiles
from core.aliases import PerformanceTable, FlowsTable
from core.preference_commons import directed_alternatives_performances
from core.sorting import pandas_check_dominance_condition


class FlowSortI:
    """
    This module computes the assignments of given alternatives to categories using FlowSort procedure based on
    PrometheeI flows.
    """

    def __init__(self,
                 categories: List[str],
                 category_profiles: PerformanceTable,
                 criteria_directions: pd.Series,
                 alternatives_flows: FlowsTable,
                 category_profiles_flows: FlowsTable,
                 comparison_with_profiles: CompareProfiles):
        """
        :param categories: List of categories names (strings only)
        :param category_profiles: Preference table with category profiles
        :param criteria_directions: Series with criteria directions
        :param alternatives_flows: Flows table with alternatives flows
        :param category_profiles_flows: Flows table with category profiles flows
        :param comparison_with_profiles: Enum CompareProfiles - indicate information of profiles types used
        in calculation.
        """
        self.categories = categories
        self.category_profiles = pd.DataFrame(directed_alternatives_performances(category_profiles.values,
                                                                                 criteria_directions.to_list()),
                                              index=category_profiles.columns, columns=category_profiles.columns)
        self.criteria_directions = criteria_directions
        self.alternatives_flows = alternatives_flows
        self.category_profiles_flows = category_profiles_flows
        self.comparison_with_profiles = comparison_with_profiles
        pandas_check_dominance_condition(self.criteria_directions, self.category_profiles)

    def __append_to_classification(self, classification: pd.DataFrame, pessimistic_category: str,
                                   optimistic_category: str, alternative_name: Hashable) -> None:

        pessimistic_category_index = self.categories.index(pessimistic_category)
        optimistic_category_index = self.categories.index(optimistic_category)

        if pessimistic_category_index > optimistic_category_index:
            classification.loc[alternative_name, optimistic_category: pessimistic_category] = True
        elif pessimistic_category_index < optimistic_category_index:
            classification.loc[alternative_name, pessimistic_category: optimistic_category] = True
        else:  # positive_category_index = negative_category_index i.e. precise assignment to a specific category
            classification.loc[alternative_name, pessimistic_category] = True

    def __limiting_profiles_sorting(self) -> pd.DataFrame:
        """
        Comparing positive and negative flows of each alternative with all limiting profiles and assign them to
        correctly class.

        :return: DataFrame with alternatives assigned to proper classes
        """

        classification = pd.DataFrame([[False for _ in self.categories] for __ in self.alternatives_flows.index],
                                      index=self.alternatives_flows.index, columns=self.categories)

        for alternative, alternative_row in self.alternatives_flows.iterrows():
            positive_flow_category = ''
            negative_flow_category = ''
            for i, category, category_row in enumerate(self.category_profiles_flows.iterrows()):
                if not positive_flow_category:
                    if category_row['positive'] < alternative_row['positive'] \
                            <= self.category_profiles_flows.iloc[i + 1]['positive']:
                        positive_flow_category = category
                if not negative_flow_category:
                    if category_row['negative'] >= alternative_row['negative'] \
                            > self.category_profiles_flows.iloc[i + 1]['negative']:
                        negative_flow_category = category
                if positive_flow_category and negative_flow_category:
                    self.__append_to_classification(classification, negative_flow_category,
                                                    positive_flow_category, alternative)
                    break

        return classification

    def __boundary_profiles_sorting(self) -> pd.DataFrame:
        """
        Comparing positive and negative flows of each alternative with all boundary profiles and assign them to
        correctly class.

        :return: DataFrame with alternatives assigned to proper classes
        """
        classification = pd.DataFrame([[False for _ in self.categories] for __ in self.alternatives_flows.index],
                                      index=self.alternatives_flows.index, columns=self.categories)

        for alternative, alternative_row in self.alternatives_flows.iterrows():
            positive_flow_category = ''
            negative_flow_category = ''
            for i, category, category_row in enumerate(self.category_profiles_flows.iterrows()):
                if not positive_flow_category:
                    if i == 0:
                        if alternative_row['positive'] <= category_row['positive']:
                            positive_flow_category = self.categories[i]
                    elif i == self.category_profiles.shape[0] - 1:
                        if alternative_row['positive'] > self.category_profiles_flows.iloc[i - 1]['positive']:
                            positive_flow_category = self.categories[i]
                    else:
                        if self.category_profiles_flows.iloc[i - 1]['positive'] < \
                                alternative_row['positive'] <= category_row['positive']:
                            positive_flow_category = self.categories[i]
                if not negative_flow_category:
                    if i == 0:
                        if alternative_row['negative'] > category_row['negative']:
                            negative_flow_category = self.categories[i]
                    elif i == len(self.category_profiles) - 1:
                        if alternative_row['negative'] <= self.category_profiles_flows.iloc[i - 1]['negative']:
                            negative_flow_category = self.categories[i]
                    else:
                        if self.category_profiles_flows.iloc[i - 1]['negative'] >= \
                                alternative_row['negative'] > category_row['negative']:
                            negative_flow_category = self.categories[i]
                if positive_flow_category and negative_flow_category:
                    self.__append_to_classification(classification, positive_flow_category, negative_flow_category,
                                                    alternative)
                    break

        return classification

    def __central_profiles_sorting(self) -> pd.DataFrame:
        """
        Comparing positive and negative flows of each alternative with all central profiles and assign them to
        correctly class.

        :return: DataFrame with alternatives assigned to proper classes
        """
        classification = pd.DataFrame([[False for _ in self.categories] for __ in self.alternatives_flows.index],
                                      index=self.alternatives_flows.index, columns=self.categories)

        for alternative, alternative_row in self.alternatives_flows.iterrows():
            positive_flow_category = ''
            negative_flow_category = ''
            for i, category, category_row in enumerate(self.category_profiles_flows.iterrows()):
                if not positive_flow_category:
                    if i == 0:
                        if alternative_row['positive'] <= \
                                (category_row['positive'] + self.category_profiles_flows.iloc[i + 1]['positive']) / 2:
                            positive_flow_category = self.categories[i]
                    elif i == len(self.category_profiles) - 1:
                        if (self.category_profiles_flows.iloc[i - 1]['positive'] + category_row['positive']) / 2 < \
                                alternative_row['positive']:
                            positive_flow_category = self.categories[i]
                    else:
                        if (self.category_profiles_flows.iloc[i - 1]['positive'] + category_row['positive']) / 2 < \
                                alternative_row['positive'] <= \
                                (category_row['positive'] + self.category_profiles_flows.iloc[i + 1]['positive']) / 2:
                            positive_flow_category = self.categories[i]
                if not negative_flow_category:
                    if i == 0:
                        if alternative_row['negative'] > \
                                (category_row['negative'] + self.category_profiles_flows.iloc[i + 1]['negative']) / 2:
                            negative_flow_category = self.categories[i]
                    elif i == len(self.category_profiles) - 1:
                        if (self.category_profiles_flows.iloc[i - 1]['negative'] + category_row['negative']) / 2 >= \
                                alternative_row['negative']:
                            negative_flow_category = self.categories[i]
                    else:
                        if (self.category_profiles_flows.iloc[i - 1]['negative'] + category_row['negative']) / 2 >= \
                                alternative_row['negative'] > \
                                (category_row['negative'] + self.category_profiles_flows.iloc[i + 1]['negative']) / 2:
                            negative_flow_category = self.categories[i]
                if positive_flow_category and negative_flow_category:
                    self.__append_to_classification(classification, positive_flow_category, negative_flow_category,
                                                    alternative)
                    break
        return classification

    def calculate_sorted_alternatives(self) -> pd.DataFrame:
        """
        Sort alternatives to proper categories.

        :return: DataFrame with alternatives assigned to proper classes
        """
        if self.comparison_with_profiles == CompareProfiles.LIMITING_PROFILES:
            return self.__limiting_profiles_sorting()
        elif self.comparison_with_profiles == CompareProfiles.BOUNDARY_PROFILES:
            return self.__boundary_profiles_sorting()
        else:
            return self.__central_profiles_sorting()
