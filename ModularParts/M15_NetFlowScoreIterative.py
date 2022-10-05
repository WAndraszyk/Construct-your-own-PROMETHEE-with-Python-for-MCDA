import numpy as np
from core.aliases import NumericValue
from core.enums import ScoringFunction, ScoringFunctionDirection
from ModularParts.M14_NetFlowScore import NetFlowScore
from typing import List


class NetFlowScoreIterative:
    """
    This class computes Net Flow Score which bases on calculating scores associated with
    each alternative and then assign to each alternative proper position in the ranking.
    """

    def __init__(self, alternatives: List[str], preferences: List[List[NumericValue]], function: ScoringFunction,
                 direction: ScoringFunctionDirection):
        """
        :param alternatives: List of alternatives names (strings only).
        :param preferences: 2D List of aggregated preferences between each alternative.
        :param function: Enum ScoringFunction - indicate which function should be used in calculating Net Flow Score.
        :param direction: Enum ScoringFunctionDirection - indicate which function direction should be used in
                          calculating Net Flow Score.
        """
        self.alternatives = alternatives
        self.preferences = np.array(preferences)
        self.NFS = NetFlowScore(preferences, function, direction)
        np.fill_diagonal(self.preferences, np.NaN)
        self.function = function
        self.direction = direction

    def create_ranking(self) -> List[str]:
        """
        Ranking creation based on the calculation of the Net Flow Score. The first item in the list is ranked first.

        :return: Ranking list of alternatives based on Net Flow Scores.
        """
        scores = self.NFS.calculate_net_flows_score(avoid_same_scores=True)

        ranking = [a for _, a in sorted(zip(scores, self.alternatives), reverse=True)]

        return ranking
