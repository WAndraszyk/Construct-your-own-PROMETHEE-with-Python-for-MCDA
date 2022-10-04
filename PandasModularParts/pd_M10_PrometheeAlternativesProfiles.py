import pandas as pd

from core.aliases import NumericValue, PerformanceTable
from typing import List, Dict


class PrometheeAlternativesProfiles:
    """
    This module profile the alternatives using the single criterion net flows.
    """

    def __init__(self,
                 alternatives: PerformanceTable,
                 criteria_weights: pd.Series,
                 partial_preferences: pd.DataFrame):
        """
        :param alternatives: List of alternatives names (strings only)
        :param criteria_weights: Series with name as index and weight of each criterion
        :param partial_preferences: DataFrame with MultiIndex of criterion and alternative and alternative as columns.
         Represents partial preferences of every alternative over others on each criterion.
        """

        self.alternatives = alternatives
        self.criteria_weights= criteria_weights
        self.partial_preferences = partial_preferences

    def __calculate_criteria_net_flows(self) -> List[List[NumericValue]]:
        """
        Calculate criteria net flows for alternatives.
        """
        n_alternatives = len(self.alternatives)

        criteria_net_flows = [[] for _ in self.alternatives]
        for criterion_i, criterion_partial_performances in enumerate(self.partial_preferences):
            for alternative_i, partial_preference_i in enumerate(criterion_partial_performances):
                criteria_net_flow = 0
                for alternative_j, partial_preference_j in enumerate(criterion_partial_performances):
                    if alternative_i != alternative_j:
                        criteria_net_flow += (partial_preference_i[alternative_j] - partial_preference_j[alternative_i])
                criteria_net_flows[alternative_i].append(1 / (n_alternatives - 1) * criteria_net_flow)

        return criteria_net_flows

    def __calculate_net_flows(self, criteria_net_flows: List[List[NumericValue]]) -> List[NumericValue]:
        """
        Aggregate single criterion net flows multiplied by weights of criterion to compute the net outranking flow.
        """

        criteria_weights = [criterion_weight for _, criterion_weight in self.criteria]

        net_flows = [sum([criterion_weight * criterion_net_flow for criterion_net_flow, criterion_weight
                          in zip(alternative_criteria_net_flows, criteria_weights)])
                     for alternative_criteria_net_flows in criteria_net_flows]

        return net_flows

    def calculate_alternatives_profiles(self) -> Dict[str, NumericValue]:
        """
        Calculate the alternatives profiles.
        """
        criteria_net_flows = self.__calculate_criteria_net_flows()
        net_flows = self.__calculate_net_flows(criteria_net_flows)

        alternatives_with_assigned_flows = {alternative: net_flow for alternative, net_flow
                                            in zip(self.alternatives, net_flows)}
        return alternatives_with_assigned_flows
