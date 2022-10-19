import numpy as np
import pandas as pd
from core.aliases import PreferencesTable
from core.enums import ScoringFunction, ScoringFunctionDirection
from ModularParts.M14_NetFlowScore import NetFlowScore


class NetFlowScoreIterative:
    """
    This class computes Net Flow Score which bases on calculating scores associated with
    each alternative and then assign to each alternative proper position in the ranking.
    """

    def __init__(self, preferences: PreferencesTable, function: ScoringFunction,
                 direction: ScoringFunctionDirection):
        """
        :param preferences: Preference table of aggregated preferences.
        :param function: Enum ScoringFunction - indicate which function should be used in calculating Net Flow Score.
        :param direction: Enum ScoringFunctionDirection - indicate which function direction should be used in
                          calculating Net Flow Score.
        """
        self.preferences = preferences
        self.NFS = NetFlowScore(preferences, function, direction)
        np.fill_diagonal(self.preferences.values, np.NaN)
        self.function = function
        self.direction = direction

    def create_ranking(self) -> pd.Series:
        """
        Ranking creation based on the calculation of the Net Flow Score. The first item in the list is ranked first.

        :return: Ranking list of alternatives based on Net Flow Scores.
        """
        scores = self.NFS.calculate_net_flows_score(avoid_same_scores=True)

        ranking = scores.sort_values(ascending=False)

        return ranking
