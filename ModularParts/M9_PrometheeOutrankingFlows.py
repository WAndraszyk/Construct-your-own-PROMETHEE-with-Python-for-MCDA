import numpy as np
from core.aliases import NumericValue
from typing import List, Tuple


class PrometheeOutrankingFlows:
    """
    This class computes positive and negative outranking flows
    based on preferences.
    """

    def __init__(self, alternatives: List[str], preferences: List[List[NumericValue]],
                 category_profiles: Tuple[List[List[NumericValue]], List[List[NumericValue]]] = None):
        """
        :param alternatives: List of alternatives names (strings only)
        :param preferences: 2D array of aggregated preferences (profile over profile )
        :param category_profiles: 2-element tuple of 2D arrays of aggregated preferences (profile over category
                                  and category over profile)
        """
        self.category_profiles = category_profiles
        self.alternatives = alternatives
        self.preferences = preferences

    def __calculate_flow(self, positive: bool = True, category_profiles: bool = False) -> List[NumericValue]:
        """
        Calculate positive or negative outranking flow.


        :param positive: if True function returns positive outranking flow
                         else returns negative outranking flow
        :param category_profiles: if True calculate flows for comparison between profiles and categories,
                                  else calculate flows for comparison between profiles.
        :return: List of outranking flow's values
        """
        if category_profiles:
            if positive:
                n = len(self.category_profiles[0])
                aggregatedPIes = np.sum(self.category_profiles[0], axis=1)
                flows = aggregatedPIes / (n - 1)
            else:
                n = len(self.category_profiles[1])
                aggregatedPIes = np.sum(self.category_profiles[1], axis=0)
                flows = aggregatedPIes / (n - 1)
        else:
            n = len(self.alternatives)

            axis = 1 if positive else 0
            aggregatedPIes = np.sum(self.preferences, axis=axis)
            flows = aggregatedPIes / (n - 1)

        return flows

    def calculate_flows(self, category_profiles: bool = False) -> Tuple[List[NumericValue], List[NumericValue]]:
        """
        Calculate both positive and negative outranking flows.

        :param category_profiles: if True calculate flows for comparison between profiles and categories,
                                  else calculate flows for comparison between profiles.
        :return:
                OUT1: positive outranking flow
                OUT2: negative outranking flow
        """
        return self.__calculate_flow(category_profiles=category_profiles), \
            self.__calculate_flow(positive=False, category_profiles=category_profiles)
