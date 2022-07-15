from core.aliases import NumericValue
from typing import List


class PrometheeIRanking:
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

    def calculate_ranking(self) -> List[List[str]]:
        """
        Calculate outranking pairs - 1st alternative in pair is weak-preferenced over 2nd alternative in pair.
        :return: List of outranking pairs
        """
        # po co ten or tutaj? Nie mozna dac >= ?
        pairs = []
        for num_a, alternative_a in enumerate(self.alternatives):
            for num_b, alternative_b in enumerate(self.alternatives):
                if self.positive_flow[num_a] > self.positive_flow[num_b] \
                        and self.negative_flow[num_a] <= self.negative_flow[num_b] \
                        or \
                        self.positive_flow[num_a] == self.positive_flow[num_b] \
                        and self.negative_flow[num_a] <= self.negative_flow[num_b]:
                    pairs.append([alternative_a, alternative_b])

        return pairs

