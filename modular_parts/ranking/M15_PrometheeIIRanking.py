"""
    This class compute PrometheeIIRanking based on promethee II flows.
"""
import pandas as pd
from core.input_validation import promethee_ii_ranking_validation
__all__ = ["calculate_promethee_ii_ranking"]


def calculate_promethee_ii_ranking(promethee_ii_flows: pd.DataFrame
                                   ) -> pd.Series:
    """
    Calculates ranking based on Promethee II net flow.

    :param promethee_ii_flows: Dataframe of positive, negative and net flows

    :return: Ranking of alternatives
    """
    promethee_ii_ranking_validation(promethee_ii_flows)
    data = promethee_ii_flows.sort_values('net', ascending=False).index
    ranking = pd.Series(data=data, name="ranking")
    ranking.index += 1
    return ranking
