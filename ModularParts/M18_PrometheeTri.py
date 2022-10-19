import pandas as pd
from core.aliases import NumericValue
from typing import List, Tuple, Dict


class PrometheeTri:
    """
    This module computes the assignments of given alternatives to categories using Promethee Tri method.
    """

    def __init__(self,
                 categories: List[str],
                 criteria_weights: pd.Series,
                 alternatives_partial_preferences: Tuple[pd.DataFrame, pd.DataFrame],
                 profiles_partial_preferences: pd.DataFrame,
                 assign_to_better_class: bool = True,
                 use_marginal_value: bool = True):
        """
        :param categories: List of categories names (strings only)
        :param criteria_weights: Series with weights of each criterion
        :param alternatives_partial_preferences: Tuple with 2 DataFrames with partial preferences (alternatives vs profiles and
        profiles vs alternatives)
        :param profiles_partial_preferences: DataFrame with partial preferences (profiles vs profiles)
        :param assign_to_better_class: Boolean which describe preference of the DM in final alternative assignment when
        deviation for two or more profiles are the same.
        :param use_marginal_value: Boolean which describe whether deviation should be
        calculated as absolute value or not
        """
        self.alternatives = alternatives_partial_preferences[1].columns.tolist()
        self.categories = categories
        self.category_profiles = profiles_partial_preferences.columuns.to_list()
        self.criteria_weights = criteria_weights
        self.alternatives_partial_preferences = alternatives_partial_preferences
        self.profiles_partial_preferences = profiles_partial_preferences
        self.assign_to_better_class = assign_to_better_class
        self.use_marginal_value = use_marginal_value

    def __calculate_criteria_net_flows(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Calculate criteria net flows for profiles and alternatives.

        :return: Tuple with 2 DataFrames with criteria net flows for profiles and alternatives
        """
        profiles_criteria_net_flows = pd.DataFrame()
        alternatives_criteria_net_flows = pd.DataFrame()

        n_profiles = len(self.category_profiles)

        for criterion, criterion_preferences in self.profiles_partial_preferences.groupby(level=0):
            for profile_i, profile_i_row, profile_j, profile_j_col \
                    in zip(criterion_preferences.droplevel(0).iterrows(),
                           criterion_preferences.droplevel(0).T.iterrows()):
                profiles_criteria_net_flows[profile_i] = (profile_i_row - profile_j_col) / (n_profiles - 1)

        profiles_criteria_net_flows = profiles_criteria_net_flows.T
        profiles_criteria_net_flows.columns = self.profiles_partial_preferences.index.get_level_values(0)
        profiles_criteria_net_flows.index = self.alternatives

        n_alternatives = len(self.alternatives)

        for (criterion, criterion_preferences1, criterion, criterion_preferences2)\
                in zip(self.alternatives_partial_preferences[0].groupby(level=0),
                       self.alternatives_partial_preferences[0].groupby(level=0)):
            for alternative_i, alternative_i_row, profile_j, profile_j_col \
                    in zip(criterion_preferences1.droplevel(0).iterrows(),
                           criterion_preferences2.droplevel(0).T.iterrows()):
                alternatives_criteria_net_flows[alternative_i] = (alternative_i_row - profile_j_col) / n_alternatives

        alternatives_criteria_net_flows = alternatives_criteria_net_flows.T
        alternatives_criteria_net_flows.columns = self.alternatives_partial_preferences[0].index.get_level_values(0)
        alternatives_criteria_net_flows.index = self.alternatives

        return profiles_criteria_net_flows, alternatives_criteria_net_flows

    def __calculate_deviations(self, profiles_criteria_net_flows: pd.DataFrame,
                               alternatives_criteria_net_flows: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate deviation for each alternative and each profile.

        :param profiles_criteria_net_flows: DataFrame with criteria net flows for profiles
        :param alternatives_criteria_net_flows: DataFrame with criteria net flows for alternatives

        :return: DataFrame with deviations
        """
        deviations = pd.DataFrame(columns=self.profiles_partial_preferences.index, index=self.alternatives)

        for alternative, alternative_row in alternatives_criteria_net_flows.iterrows():
            for profile, profile_row in profiles_criteria_net_flows.iterrows():
                if self.use_marginal_value:
                    deviations[profile][alternative] = abs(alternative_row - profile_row).sum()
                else:
                    deviations[profile][alternative] = (self.criteria_weights * (alternative_row - profile_row)).sum()

        return deviations

    def __assign_alternatives_to_classes_with_minimal_deviation(self, deviations: pd.DataFrame) -> pd.Series:
        """
        Assign every alternative to class with minimal deviation for pair alternative, class.

        :param deviations: DataFrame with deviations

        :return: Series with precise assignments of alternatives to categories
        """
        classification = pd.Series(index=self.alternatives)
        for alternative, alternative_row in deviations.iterrows():
            if self.assign_to_better_class:
                classification[alternative] = alternative_row.contains(alternative_row.min()).idxmax()
            else:
                classification[alternative] = alternative_row.contains(alternative_row.min()).idxmin()

        return classification

    def calculate_sorted_alternatives(self) -> pd.Series:
        """
        Sort alternatives to proper categories.

        :return: Series with precise assignments of alternatives to categories
        """
        profiles_criteria_net_flows, alternatives_criteria_net_flows = self.__calculate_criteria_net_flows()
        deviations = self.__calculate_deviations(profiles_criteria_net_flows, alternatives_criteria_net_flows)
        return self.__assign_alternatives_to_classes_with_minimal_deviation(deviations)
