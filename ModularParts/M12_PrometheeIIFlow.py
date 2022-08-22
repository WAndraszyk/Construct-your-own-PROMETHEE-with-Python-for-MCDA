from core.aliases import NumericValue
from typing import List


class PrometheeIIFlow:
    """
    This class compute net outranking flow for PrometheeII based on positive and negative flows.
    'Net outranking flow' is a difference between positive and negative flow for each alternative.
    """

    def __init__(self,  positive_flow: List[NumericValue], negative_flow: List[NumericValue]):
        """
        :param positive_flow: List of positive flow values
        :param negative_flow: List of negative flow values
        """
        self.positive_flow = positive_flow
        self.negative_flow = negative_flow

    def calculate_PrometheeIIFlow(self):
        """
        Calculates net outranking flow.
        :return: net outranking flow as a list.
        """
        flow = []
        for num_a, alternative_a in enumerate(self.positive_flow):
            flow.append(self.positive_flow[num_a] - self.negative_flow[num_a])
        return flow
