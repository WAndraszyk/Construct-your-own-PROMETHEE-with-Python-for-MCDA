import pandas as pd

__all__ = ["calculate_promethee_ii_ranking"]


def calculate_promethee_ii_ranking(promethee_ii_flows: pd.DataFrame) -> pd.Series:
    data = promethee_ii_flows.sort_values('net', ascending=False).index
    ranking = pd.Series(data=data, name="ranking")
    ranking.index += 1
    return ranking
