import pandas as pd


class PrometheeAlternativesProfiles:
    """
    This module profile the alternatives using the single criterion net flows.
    """

    def __init__(self,
                 criteria_weights: pd.Series,
                 partial_preferences: pd.DataFrame):
        """
        :param criteria_weights: Series with name as index and weight of each criterion
        :param partial_preferences: DataFrame with MultiIndex of criterion and alternative and alternative as columns.
         Represents partial preferences of every alternative over others on each criterion.
        """

        self.alternatives = partial_preferences.columns.tolist()
        self.criteria_weights = criteria_weights
        self.partial_preferences = partial_preferences

    def __calculate_criteria_net_flows(self) -> pd.DataFrame:
        """
        Calculate criteria net flows for alternatives.

        return: DataFrame with criteria net flows
        """

        criteria_net_flows = pd.DataFrame()
        n_alternatives = len(self.alternatives)

        for criterion, criterion_preferences in self.partial_preferences.groupby(level=0):
            for alternative_i, alternative_i_row, alternative_j, alternative_j_col \
                    in zip(criterion_preferences.droplevel(0).iterrows(),
                           criterion_preferences.droplevel(0).T.iterrows()):
                criteria_net_flows[alternative_i] = (alternative_i_row - alternative_j_col) / (n_alternatives - 1)

        criteria_net_flows = criteria_net_flows.T
        criteria_net_flows.columns = self.partial_preferences.index.get_level_values(0)
        criteria_net_flows.index = self.alternatives

        return criteria_net_flows

    def __calculate_net_flows(self, criteria_net_flows: pd.DataFrame) -> pd.Series:
        """
        Aggregate single criterion net flows multiplied by weights of criterion to compute the net outranking flow.

        return: Series with aggregated net flows
        """
        not_aggregated_net_flows = criteria_net_flows.mul(self.criteria_weights)
        net_flows = not_aggregated_net_flows.sum(axis=1)

        return net_flows

    def calculate_alternatives_profiles(self) -> pd.Series:
        """
        Calculate the alternatives profiles.

        return: Series with alternatives profiles
        """
        criteria_net_flows = self.__calculate_criteria_net_flows()
        net_flows = self.__calculate_net_flows(criteria_net_flows)

        return net_flows
