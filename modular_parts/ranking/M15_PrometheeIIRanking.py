import pandas as pd
from core.input_validation import promethee_ii_ranking_validation
__all__ = ["calculate_promethee_ii_ranking"]


def calculate_promethee_ii_ranking(promethee_ii_flows: pd.DataFrame
                                   ) -> pd.Series:
    promethee_ii_ranking_validation(promethee_ii_flows)
    data = promethee_ii_flows.sort_values('net', ascending=False).index
    ranking = pd.Series(data=data, name="ranking")
    ranking.index += 1
    return ranking
