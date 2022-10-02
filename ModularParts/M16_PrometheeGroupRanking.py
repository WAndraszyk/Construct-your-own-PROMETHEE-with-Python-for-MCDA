import numpy as np
from core.aliases import NumericValue
from typing import List, Tuple


class PrometheeGroupRanking:
    """
    This class calculates aggregated flows which are weighted sum of flows for every alternative.
    Allows many Decision Makers to get influence on final flows.
    """

    def __init__(self, alternatives: List[str], flows: List[List[NumericValue]], weights_dms: List[NumericValue]):
        """
        :param alternatives: List of alternatives names
        :param flows: List of Lists of flows (one list with flows per DM)
        :param weights_dms: List of weights of every Decision Maker. The greater the weight
         the greater the influence of DM on the output flow.
        """
        self.alternatives = alternatives
        self.flows = np.array(flows)
        self.weightsDMs = np.array(weights_dms)

    def __calculate_weighted_flows(self) -> np.ndarray:
        """
        Calculates weighted flows by multiplying flows by each DM weight.
        :return: ndarray(2 dim) of weighted flows
        """
        return np.multiply(self.weightsDMs, self.flows.T).T

    def calculate_group_ranking(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculates aggregated flows.
        :return: Tuple of ndarray(2 dim) of aggregated flows and ndarray(2 dim) of weighted flows
        """
        weighted_flows = self.__calculate_weighted_flows()
        aggregated_flows = np.sum(weighted_flows, axis=0)

        return aggregated_flows, weighted_flows
