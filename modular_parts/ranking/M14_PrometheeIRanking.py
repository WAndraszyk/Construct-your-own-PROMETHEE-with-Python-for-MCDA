"""
    This class compute PrometheeIRanking based on positive and negative flows.
    Implemented method is generalized to relation of the weak preference.
"""
import math

import pandas as pd
from core.input_validation import promethee_i_ranking_validation


__all__ = ["calculate_prometheeI_ranking"]


def calculate_prometheeI_ranking(flows: pd.DataFrame,
                                 weak_preference=True
                                 ) -> pd.DataFrame:
    """
    Calculate outranking pairs - 1st alternative in pair | relation between
    variants | 2nd alternative in pair.
    Relationship types:
        P - preferred
        I - indifferent
        ? - incomparable
        S - outranking relation

    :param flows: FlowsTable with positive and negative flows
    :param weak_preference: If True the general method of computing
    the ranking is  generalized to the relation of the weak preference
    :return: List of preference ranking pairs (alternative, relation,
     alternative)
    """
    promethee_i_ranking_validation(flows, weak_preference)

    alternatives = flows.index
    positive_flow = flows['positive']
    negative_flow = flows['negative']

    pairs = pd.DataFrame(index=alternatives, columns=alternatives)

    for alternative_a in alternatives:
        for alternative_b in alternatives:
            if alternative_a == alternative_b:
                pairs[alternative_b][alternative_a] = None
                continue
            if weak_preference:
                if positive_flow[alternative_a] >= \
                        positive_flow[alternative_b] \
                        and negative_flow[alternative_a] <= \
                        negative_flow[alternative_b]:
                    pairs[alternative_b][alternative_a] = 'S'
                else:
                    pairs[alternative_b][alternative_a] = '?'
            else:
                if math.isclose(positive_flow[alternative_a],
                                positive_flow[alternative_b]) \
                        and math.isclose(negative_flow[alternative_a],
                                         negative_flow[alternative_b]):
                    pairs[alternative_b][alternative_a] = 'I'
                elif positive_flow[alternative_a] >= \
                        positive_flow[alternative_b] \
                        and negative_flow[alternative_a] <= \
                        negative_flow[alternative_b]:
                    pairs[alternative_b][alternative_a] = 'P'
                else:
                    pairs[alternative_b][alternative_a] = '?'

    return pairs
