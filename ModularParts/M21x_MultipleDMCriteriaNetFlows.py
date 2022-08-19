from core.aliases import NumericValue
from typing import List, Tuple


class MultipleDMUniNetFlows:
    """
    Extra module for calculating GDSS flows for FlowSortGDSS.
    """
    def __init__(self,
                 alternatives: List[str],
                 category_profiles: List[str],
                 DMs_profiles_partial_preferences: List[List[List[List[NumericValue]]]],  # P(r,a)
                 DMs_alternatives_partial_preferences: List[List[List[List[NumericValue]]]],  # P(a,r)
                 DMs_profile_vs_profile_partial_preferences: List[List[List[List[NumericValue]]]],  # P(r_i,r_j)
                 criteria_weights: List[NumericValue]):
        """
        :param alternatives: List of names of alternatives
        :param category_profiles: List of names of category profiles
        :param DMs_profiles_partial_preferences: List of partial preferences profiles vs alternatives.
         Nesting order: DM, criterion, profile, alternative
        :param DMs_alternatives_partial_preferences: List of partial preferences alternatives vs profiles.
         Nesting order: DM, criterion, alternative, profile
        :param DMs_profile_vs_profile_partial_preferences: List of partial preferences profiles vs profiles.
         Nesting order: DM, criterion, profile_i, profile_j
         :param criteria_weights: List of numeric value weights for each criterion
        """
        self.alternatives = alternatives
        self.category_profiles = category_profiles
        self.DMs_profiles_partial_preferences = DMs_profiles_partial_preferences
        self.DMs_alternatives_partial_preferences = DMs_alternatives_partial_preferences
        self.DMs_profile_vs_profile_partial_preferences = DMs_profile_vs_profile_partial_preferences
        self.criteria_weights = criteria_weights

    def __calculate_alternatives_general_net_flows(self) -> List[NumericValue]:
        """
        First calculate net flows for each alternative, each profile and each criterion,
         then accumulate criteria values to global alternative net flows.

        :return: List of global net flows (for each alternative)
        """
        alternatives_net_flows = []
        n_profiles = len(self.category_profiles) * len(self.DMs_profiles_partial_preferences)

        for alternative_i, _ in enumerate(self.alternatives):
            alternative_net_flow = []
            for criterion_j, _ in enumerate(self.criteria_weights):
                net_flow = 0
                for alternative_preferences, profile_preferences in zip(self.DMs_alternatives_partial_preferences,
                                                                        self.DMs_profiles_partial_preferences):
                    for profile_k, _ in enumerate(profile_preferences[0]):
                        net_flow += alternative_preferences[criterion_j][alternative_i][profile_k] - \
                                    profile_preferences[criterion_j][profile_k][alternative_i]
                net_flow /= n_profiles
                alternative_net_flow.append(net_flow)
            alternatives_net_flows.append(alternative_net_flow)

        alternatives_general_net_flows = [sum([criterion_weight * net_flow for criterion_weight, net_flow in
                                               zip(self.criteria_weights, alternative_net_flow)])
                                          for alternative_net_flow in alternatives_net_flows]

        return alternatives_general_net_flows

    def __calculate_profiles_general_net_flows(self) -> List[List[List[NumericValue]]]:
        """
        First calculate net flows for each alternative, each DM, each category profile and each criterion,
         then accumulate criteria values to global profiles net flows.

        :return: List of global profiles net flows. Nesting order: alternative, DM, profile
        """
        profiles_net_flows = []
        n_profiles = len(self.category_profiles) * len(self.DMs_profiles_partial_preferences)

        for alternative_i, _ in enumerate(self.alternatives):
            profile_alternative_net_flows = []
            for DM_i, _ in enumerate(self.DMs_profiles_partial_preferences):
                profile_alternative_DM_net_flows = []
                for profile_i, _ in enumerate(self.category_profiles):
                    profile_alternative_DM_category_profile_net_flows = []
                    for criterion_i, _ in enumerate(self.criteria_weights):
                        net_flow = 0
                        net_flow += self.DMs_profiles_partial_preferences[DM_i][criterion_i][profile_i][alternative_i] - \
                                    self.DMs_alternatives_partial_preferences[DM_i][criterion_i][alternative_i][
                                        profile_i]
                        for profile_j, _ in enumerate(self.category_profiles):
                            for DM_j, _ in enumerate(self.DMs_profiles_partial_preferences):
                                net_flow += \
                                    self.DMs_profile_vs_profile_partial_preferences[DM_i][criterion_i][profile_i][
                                        profile_j] - \
                                    self.DMs_profile_vs_profile_partial_preferences[DM_j][criterion_i][profile_j][
                                        profile_i]
                        net_flow /= (n_profiles + 1)
                        profile_alternative_DM_category_profile_net_flows.append(net_flow)
                    profile_alternative_DM_net_flows.append(profile_alternative_DM_category_profile_net_flows)
                profile_alternative_net_flows.append(profile_alternative_DM_net_flows)
            profiles_net_flows.append(profile_alternative_net_flows)

        profiles_general_net_flows = [
            [
                [sum([criterion_weight * net_flow for criterion_weight, net_flow in
                      zip(self.criteria_weights, profile_alternative_DM_category_profile_net_flows)])
                 for profile_alternative_DM_category_profile_net_flows in profile_alternative_DM_net_flows]
                for profile_alternative_DM_net_flows in profile_alternative_net_flows]
            for profile_alternative_net_flows in profiles_net_flows]

        return profiles_general_net_flows

    def calculate_GDSS_flows(self) -> Tuple[List[NumericValue], List[List[List[NumericValue]]]]:
        """
        Calculate alternatives general net flows and profiles general net flows which are necessary
        in FlowSortGDSS method.

        :return: alternatives general net flows(List of net flows for each alternative) \
        and profiles general net flows(3D List of net flows for each alternative, DM and category_profile)
        """
        alternatives_general_net_flows = self.__calculate_alternatives_general_net_flows()
        profiles_general_net_flows = self.__calculate_profiles_general_net_flows()

        return alternatives_general_net_flows, profiles_general_net_flows
