import numpy as np

class PrometheeOutrankingFlows:
    """
    This class computes positive and negative outranking flows
    based on preferences.
    """
    def __init__(self, alternatives, preferences):
        """
        :param alternatives: List of alternatives names (strings only)
        :param preferences: 2D array of aggregated preferences
        """
        self.alternatives = alternatives
        self.preferences = preferences

    def __calculate_flow(self, positive=True):
        """
        Calculate positive or negative outranking flow.

        :param positive: if True function returns positive outranking flow
        else returns negative outranking flow
        :return: List of outranking flow's values
        """
        n = len(self.alternatives)

        axis = 1 if positive else 0
        aggregtedPIes = np.sum(self.preferences, axis=axis)
        flows = aggregtedPIes/(n-1)

        return flows
        # return np.sum(self.preferences, axis=1 if positive else 0)/(len(self.alternatives)-1)

    def calculate_flows(self):
        """
        Calculate both positive and negative outranking flows.
        :return: OUT1: positive outranking flow
                 OUT2: negative outranking flow
        """
        return self.__calculate_flow(), self.__calculate_flow(positive=False)



