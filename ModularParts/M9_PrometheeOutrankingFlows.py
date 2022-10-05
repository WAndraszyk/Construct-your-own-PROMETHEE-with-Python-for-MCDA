import numpy as np
from core.aliases import NumericValue
from typing import List, Tuple, Union


class PrometheeOutrankingFlows:
    """
    This class computes positive and negative outranking flows
    based on preferences.
    """

    def __init__(self, alternatives: List[str],
                 preferences: Union[List[List[NumericValue]],
                                    Tuple[List[List[NumericValue]], List[List[NumericValue]]]],
                 category_profiles: List[str] = None):
        """
        :param alternatives: List of alternatives names (strings only).
        :param preferences: 2D array of aggregated preferences (profile over profile ) or 2-element tuple of 2D arrays
        of aggregated preferences (profile over category and category over profile).
        :param category_profiles: List of category profiles names (stings only).
        """
        self.category_profiles = category_profiles
        self.alternatives = alternatives
        self.preferences = preferences

    def __calculate_flow(self, positive: bool = True) -> List[NumericValue]:
        """
        Calculate positive or negative outranking flow.

        :param positive: If True function returns positive outranking flow
                         else returns negative outranking flow.
        :return: List of outranking flow's values.
        """
        if isinstance(self.preferences, tuple):  # check if self.preferences are with category profiles
            if positive:
                flows = np.mean(self.preferences[0], axis=1)
            else:
                flows = np.mean(self.preferences[1], axis=0)
        else:
            n = len(self.alternatives)

            axis = 1 if positive else 0
            aggregated_preferences = np.sum(self.preferences, axis=axis)
            flows = aggregated_preferences / (n - 1)

        return flows

    def calculate_flows(self) -> Tuple[List[NumericValue], List[NumericValue]]:
        """
        Calculate both positive and negative outranking flows.

        :return:
                OUT1: positive outranking flow.
                OUT2: negative outranking flow.
        """
        return self.__calculate_flow(), self.__calculate_flow(positive=False)
