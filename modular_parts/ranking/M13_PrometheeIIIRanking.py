"""
This class computes Promethee III intervals and ranking based on positive and negative flows,
and preferences.
"""
from typing import List

import pandas as pd
from core.aliases import FlowsTable, PreferencesTable, NumericValue
import numpy as np

__all__ = ["calculate_promethee_iii_ranking"]


def calculate_promethee_iii_ranking(flows: FlowsTable, preferences: PreferencesTable,
                                    alpha: NumericValue) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculates intervals and outranking pairs:
    1st alternative in pair | relation between variants | 2nd alternative in pair.
    Relationship types:
    P - preferred
    I - indifferent

    :param flows: FlowsTable of both positive and negative outranking flows.
    :param preferences: PreferenceTable of alternatives over alternatives
    :param alpha: parameter used in calculating intervals

    :return: Intervals; Preference ranking pairs
    """

    alternatives = preferences.index
    preferences = preferences
    flow = np.subtract(flows['positive'].values, flows['negative'].values)

    if alpha <= 0:
        raise Exception("Alpha has to be greater than 0")
    intervals_list, intervals = _calculate_intervals(alternatives, flow, preferences, alpha)
    pairs_data = np.zeros(np.shape(preferences), dtype=str)
    for num_a in range(len(alternatives)):
        for num_b in range(len(alternatives)):
            if intervals_list[0][num_a] > intervals_list[1][num_b]:
                pairs_data[num_a][num_b] = 'P'
            elif intervals_list[0][num_a] <= intervals_list[1][num_b] \
                    and intervals_list[0][num_b] <= intervals_list[1][num_a]:
                pairs_data[num_a][num_b] = 'I'
            else:
                pairs_data[num_a][num_b] = '?'

    pairs = pd.DataFrame(data=pairs_data, columns=alternatives, index=alternatives)

    return intervals, pairs


def _calculate_intervals(alternatives, flow: FlowsTable, preferences: PreferencesTable, alpha: NumericValue
                         ) -> tuple[List[List[NumericValue]], pd.DataFrame]:
    """
    Calculates intervals used in alternatives comparison.

    :param alpha: parameter used in calculating intervals

    :return: intervals in a list, intervals as a DataFrame
    """
    sigmas = []
    n = len(alternatives)
    for i in preferences.index:
        total = 0
        for j in preferences.columns:
            total += np.square(preferences.loc[i, j] - preferences.loc[j, i] - flow[i])
        sigma = np.sqrt((1 / n) * total)
        sigmas.append(sigma)

    x = []
    y = []
    for i in range(n):
        xi = flow[i] - alpha * sigmas[i]
        x.append(xi)
        yi = flow[i] + alpha * sigmas[i]
        y.append(yi)

    intervals = {'x': x, 'y': y}

    return [x, y], pd.DataFrame(intervals, index=alternatives)
