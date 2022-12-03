"""
    This class computes Net Flow Score which bases on calculating scores associated with
    each alternative and then assign to each alternative proper position in the ranking.
"""
import pandas as pd
from core.aliases import PreferencesTable
from core.enums import ScoringFunction, ScoringFunctionDirection
from core.input_validation import net_flow_score_iterative_validation
from modular_parts.flows import calculate_net_flows_score

__all__ = ['calculate_netflow_score_ranking']


def calculate_netflow_score_ranking(preferences: PreferencesTable,
                                    function: ScoringFunction,
                                    direction: ScoringFunctionDirection,
                                    avoid_same_scores: bool = True) -> pd.Series:
    """
    Ranking creation based on the calculation of the Net Flow Score. The first item in the list is ranked first.

    :param preferences: Preference table of aggregated preferences.
    :param function: Enum ScoringFunction - indicate which function should be used in calculating Net Flow Score.
    :param direction: Enum ScoringFunctionDirection - indicate which function direction should be used in
                      calculating Net Flow Score.
    :param avoid_same_scores: If True and calculate_scores returns some equal scores calculate once more scores for
                      alternatives which get the same score.

    :return: Ranking list of alternatives based on Net Flow Scores.
    """
    net_flow_score_iterative_validation(preferences, function, direction, avoid_same_scores)

    scores = calculate_net_flows_score(preferences, function, direction, avoid_same_scores=avoid_same_scores)

    ranking = scores.sort_values(ascending=False)

    return ranking
