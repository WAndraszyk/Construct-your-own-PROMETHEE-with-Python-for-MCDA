from core.aliases import NumericValue
from typing import List


class PrometheeIIFlow:
    """
    This class compute PrometheeIRanking based on positive and negative flows.
    Implemented method is generalized to relation of the weak preference.
    """

    def __init__(self, alternatives: List[str], positive_flow: List[NumericValue], negative_flow: List[NumericValue]):
        """
        :param alternatives: List of alternatives names (strings only)
        :param positive_flow: List of positive flow values
        :param negative_flow: List of negative flow values
        """
        self.alternatives = alternatives
        self.positive_flow = positive_flow
        self.negative_flow = negative_flow

    def calculate_PrometheeIIFlow(self):
        flow = []
        for num_a, alternative_a in enumerate(self.alternatives):
            flow.append(self.positive_flow[num_a] - self.negative_flow[num_a])
        return flow
