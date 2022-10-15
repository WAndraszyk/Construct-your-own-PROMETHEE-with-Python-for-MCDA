import pandas as pd

from core.aliases import NumericValue
from typing import List, Tuple


class MultipleDMUniNetFlows:
    """
    Extra module for calculating GDSS flows for FlowSortGDSS.
    """

    def __init__(self,
                 dms_profiles_partial_preferences: List[pd.DataFrame],  # P(r,a)
                 dms_alternatives_partial_preferences: List[pd.DataFrame],  # P(a,r)
                 dms_profile_vs_profile_partial_preferences: pd.DataFrame,  # P(r_i,r_j)
                 criteria_weights: pd.Series):
        """
        :param dms_profiles_partial_preferences: List of partial preferences profiles vs alternatives.
         MultiIndex: DM, criterion, profile; Column: alternative
        :param dms_alternatives_partial_preferences: List of partial preferences alternatives vs profiles.
         Nesting order: DM, criterion, alternative, profile
        :param dms_profile_vs_profile_partial_preferences: DataFrame with partial preferences profiles vs profiles
         between any DM. Nesting order: DM, criterion, profile_i, profile_j
        :param criteria_weights: List of numeric value weights for each criterion
        """
        self.alternatives = dms_profiles_partial_preferences[0].columns
        self.category_profiles = dms_alternatives_partial_preferences[0].columns
        self.DMs_profiles_partial_preferences = dms_profiles_partial_preferences
        self.DMs_alternatives_partial_preferences = dms_alternatives_partial_preferences
        self.DMs_profile_vs_profile_partial_preferences = dms_profile_vs_profile_partial_preferences
        self.criteria_weights = criteria_weights

    def __calculate_alternatives_general_net_flows(self) -> pd.Series:
        """
        First calculate net flows for each alternative, each profile and each criterion,
         then accumulate criteria values to global alternative net flows.

        :return: Series with global net flows (for each alternative)
        """
        alternatives_net_flows = pd.Series(index=self.alternatives)

        n_profiles = len(self.category_profiles) * len(self.DMs_profiles_partial_preferences)

        for alternatives_partial_preferences, profiles_partial_preferences \
                in zip(self.DMs_alternatives_partial_preferences, self.DMs_profiles_partial_preferences):

            for (criterion, criterion_preferences1, criterion, criterion_preferences2) \
                    in zip(alternatives_partial_preferences.groupby(level=0),
                           profiles_partial_preferences.groupby(level=0)):
                for alternative_i, alternative_i_row, profile_j, profile_j_col \
                        in zip(criterion_preferences1.droplevel(0).iterrows(),
                               criterion_preferences2.droplevel(0).T.iterrows()):
                    alternatives_net_flows[alternative_i] += alternative_i_row - profile_j_col

        alternatives_net_flows /= n_profiles

        return alternatives_net_flows

    def __calculate_profiles_general_net_flows(self) -> List[List[List[NumericValue]]]:
        """
        First calculate net flows for each alternative, each DM, each category profile and each criterion,
         then accumulate criteria values to global profiles net flows.

        :return: List of global profiles net flows. Nesting order: alternative, DM, profile
        """
        profiles_net_flows = []
        n_profiles = self.DMs_profile_vs_profile_partial_preferences.shape[0]



        for i, DM_i_df in enumerate(self.DMs_profile_vs_profile_partial_preferences):
            dm_alternatives_partial_preferences = self.DMs_alternatives_partial_preferences[i]
            dm_profiles_partial_preferences = self.DMs_profiles_partial_preferences[i]
            for DM_i_index, criterion_i, profiles_partial_preferences_i in DM_i_df.groupby([0, 1]):
                dm_profile_net_flows = pd.Series(index=[DM_i_index, criterion_i, profiles_partial_preferences_i.index])
                for _, criterion_preferences1, _, criterion_preferences2 in zip(
                        dm_alternatives_partial_preferences.groupby([0, 1]),
                        dm_profiles_partial_preferences.groupby([0, 1])):
                    for DM_j_df in self.DMs_profile_vs_profile_partial_preferences:
                        for DM_j_index, criterion_j, profiles_partial_preferences_j in DM_j_df.groupby([0, 1]):
                            for profile_i, profile_i_row, profile_j, profile_j_col \
                                    in zip(profiles_partial_preferences_i.droplevel(0).iterrows(),
                                           profiles_partial_preferences_j.droplevel(0).T.iterrows()):
                                dm_profile_net_flows[DM_i_index, criterion_i, profile_i] += \
                                    profile_i_row - profile_j_col

        # Old sum
        # profiles_general_net_flows = [
        #     [[sum([criterion_weight * net_flow for criterion_weight, net_flow in
        #            zip(self.criteria_weights, profile_alternative_DM_category_profile_net_flows)])
        #       for profile_alternative_DM_category_profile_net_flows in profile_alternative_DM_net_flows]
        #      for profile_alternative_DM_net_flows in profile_alternative_net_flows]
        #     for profile_alternative_net_flows in profiles_net_flows]

        return profiles_net_flows

    def calculate_gdss_flows(self) -> Tuple[List[NumericValue], List[List[List[NumericValue]]]]:
        """
        Calculate alternatives general net flows and profiles general net flows which are necessary
        in FlowSortGDSS method.

        :return: alternatives general net flows(List of net flows for each alternative) \
        and profiles general net flows(3D List of net flows for each alternative, DM and category_profile)
        """
        alternatives_general_net_flows = self.__calculate_alternatives_general_net_flows()
        profiles_general_net_flows = self.__calculate_profiles_general_net_flows()

        return alternatives_general_net_flows, profiles_general_net_flows
