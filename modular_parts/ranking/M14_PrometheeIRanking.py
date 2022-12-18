"""
    This class compute PrometheeIRanking based on positive and negative flows.
    Implemented method is generalized to relation of the weak preference.

    Implementation and naming of conventions are taken from
    :cite:p:'BransMareschal2005'.
"""
import math

import pandas as pd
from typing import List, Tuple
from core.input_validation import promethee_i_ranking_validation
from core.enums import RelationType
# from mcda.core.sorting import RelationType -> ścieżka francuza


__all__ = ["calculate_prometheeI_ranking"]


def calculate_prometheeI_ranking(flows: pd.DataFrame,
                                 weak_preference=False
                                 ) -> List[Tuple[str, str, RelationType]]:
    """
    This function calculates outranking pairs - 1st alternative in pair |
    2nd alternative in pair | relation between variants.
    Relationship types:
        PREFERENCE,
        INDIFFERENCE,
        INCOMPARABLE,
        WEAK_PREFERENCE.

    :param flows: pd.DataFrame with alternatives names as index and flows
    as columns named (positive and negative)
    :param weak_preference: bool that determines if general method of
    computing the ranking is  generalized to the relation of the
    weak preference

    :return: List with outranking pars (str, str, RelationType)
    """
    promethee_i_ranking_validation(flows, weak_preference)

    alternatives = flows.index
    positive_flow = flows['positive']
    negative_flow = flows['negative']

    pairs = []

    # Outranking relation among all alternatives calculation
    for alternative_a in alternatives:
        for alternative_b in alternatives:
            if alternative_a == alternative_b:
                continue
            if weak_preference:
                if positive_flow[alternative_a] >= \
                        positive_flow[alternative_b] \
                        and negative_flow[alternative_a] <= \
                        negative_flow[alternative_b]:
                    pairs.append((alternative_a, alternative_b,
                                  RelationType.WEAK_PREFERENCE))
                else:
                    pairs.append((alternative_a, alternative_b,
                                  RelationType.INCOMPARABLE))
            else:
                if math.isclose(positive_flow[alternative_a],
                                positive_flow[alternative_b], rel_tol=1e-6) \
                        and math.isclose(negative_flow[alternative_a],
                                         negative_flow[alternative_b]):
                    pairs.append((alternative_a, alternative_b,
                                  RelationType.INDIFFERENCE))

                elif positive_flow[alternative_a] >= \
                        positive_flow[alternative_b] \
                        and negative_flow[alternative_a] <= \
                        negative_flow[alternative_b]:
                    pairs.append((alternative_a, alternative_b,
                                  RelationType.PREFERENCE))
                else:
                    pairs.append((alternative_a, alternative_b,
                                  RelationType.INCOMPARABLE))

    return pairs
