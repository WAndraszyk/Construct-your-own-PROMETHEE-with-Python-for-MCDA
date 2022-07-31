from core.aliases import NumericValue
from typing import List


class PrometheeIIIFlow:
    """
        This class computes Promethee III intervals and ranking based on positive and negative flows,
        and preferences.
        """

    def __init__(self, alternatives: List[str], positive_flow: List[NumericValue], negative_flow: List[NumericValue],
                 preferences: List[List[NumericValue]]):
        """
        :param alternatives: List of alternatives names (strings only)
        :param positive_flow: List of positive flow values
        :param negative_flow: List of negative flow values
        :param preferences: List of preference of every alternative over others
        """
        self.alternatives = alternatives
        self.positive_flow = positive_flow
        self.negative_flow = negative_flow
        self.preferences = preferences
