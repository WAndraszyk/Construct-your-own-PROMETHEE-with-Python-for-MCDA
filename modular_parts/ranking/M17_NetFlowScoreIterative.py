"""
    This class computes Net Flow Score which bases on calculating scores
    associated with each alternative and then assign to each alternative
    proper position in the ranking.

    Implementation and naming conventions are taken from
    :cite:p:'KadzinskiMichalski2016'
"""
import pandas as pd
from core.enums import ScoringFunction, ScoringFunctionDirection
from core.input_validation import net_flow_score_iterative_validation
from modular_parts.flows import calculate_net_flows_score

__all__ = ['calculate_netflow_score_ranking']


def calculate_netflow_score_ranking(preferences: pd.DataFrame,
                                    function: ScoringFunction,
                                    direction: ScoringFunctionDirection
                                    ) -> pd.Series:
    """
    Ranking creation based on the calculation of the Net Flow Score.
    The first item in the list is ranked first.

    :param preferences: pd.DataFrame with alternatives as index and
    alternatives as index
    :param function: ScoringFunction object, which defines the function
    used to calculate the score
    :param direction: ScoringFunctionDirection object, which defines the
    direction of the function

    :return: pd.Series with alternatives as index and net flow score
    as values. Object is sorted in descending order.
    """

    # Input validation
    net_flow_score_iterative_validation(preferences, function, direction)

    # Use net flow score module for calculations
    scores = calculate_net_flows_score(preferences, function, direction,
                                       avoid_same_scores=True)
    # Sort the ranking
    ranking = scores.sort_values(ascending=False)

    return ranking
