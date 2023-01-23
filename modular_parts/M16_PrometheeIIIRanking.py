"""
.. image:: prometheePUT_figures/M16.jpg

This class computes Promethee III intervals and ranking based on positive
and negative flows and preferences.

Implementation and naming of conventions are taken from
:cite:p:`PrometheeIII`.
"""
from typing import List, Tuple

import numpy as np
import pandas as pd

from core.enums import RelationType
from core.input_validation.ranking import promethee_iii_ranking_validation

__all__ = ["calculate_promethee_iii_ranking"]


def calculate_promethee_iii_ranking(
    flows: pd.DataFrame,
    preferences: pd.DataFrame,
    alpha: float,
    decimal_place: int = 3,
) -> Tuple[pd.DataFrame, List[Tuple[str, str, RelationType]]]:
    """
    Calculates intervals and outranking pairs:
    1st alternative in pair | relation between variants | 2nd alternative
    in pair.
    Relationship types:

    P - preferred

    I - indifferent

    :param flows: DataFrame of both positive and negative outranking flows.
        Index: alternatives, columns: flows type.
    :param preferences: DataFrame of preference indices with alternatives as
        index and columns.
    :param alpha: parameter used in calculating intervals
    :param decimal_place: the decimal place of the output numbers

    :return: DataFrame of intervals with alternatives as index and
         x, y intervals as columns; List with tuples(str, str, RelationType)
         with outranking pairs and relation between them
    """
    # input data validation
    promethee_iii_ranking_validation(flows, preferences, alpha, decimal_place)

    alternatives = preferences.index

    # calculate net flows
    flow = pd.Series(
        data=np.subtract(flows["positive"].values, flows["negative"].values),
        index=alternatives,
    )

    # calculate intervals
    intervals_list, intervals = _calculate_intervals(
        alternatives, flow, preferences, alpha, decimal_place
    )

    outranking_pairs = []
    for i, a1 in enumerate(alternatives):
        for j, a2 in enumerate(alternatives):
            if a1 == a2:
                continue
            # compare alternatives' intervals
            if intervals_list[0][i] > intervals_list[1][j]:
                outranking_pairs.append((a1, a2, RelationType.PREFERENCE))
            elif (
                intervals_list[0][i] <= intervals_list[1][j]
                and intervals_list[0][j] <= intervals_list[1][i]
            ):
                outranking_pairs.append((a1, a2, RelationType.INDIFFERENCE))
            else:
                outranking_pairs.append((a1, a2, RelationType.INCOMPARABLE))

    return intervals, outranking_pairs


def _calculate_intervals(
    alternatives: pd.Index,
    flow: pd.Series,
    preferences: pd.DataFrame,
    alpha: float,
    decimal_place: int = 3,
) -> Tuple[List[List[float]], pd.DataFrame]:
    """
    Calculates intervals used in alternatives comparison.

    :param alternatives: list of alternatives
    :param flow: Series of net flows with alternatives as index
    :param preferences: DataFrame of preference indices with alternatives as
        index and columns.
    :param alpha: parameter used in calculating intervals
    :param decimal_place: the decimal place of the output numbers

    :return: intervals x, y in a matrix;  DataFrame of intervals with
        alternatives as index and x, y intervals as columns
    """
    # calculate sigma values
    sigmas = []
    n = len(alternatives)
    for i in preferences.index:
        total = 0
        for j in preferences.columns:
            total += np.square(preferences.loc[i, j] - preferences.loc[j, i] - flow[i])
        sigma = np.sqrt((1 / n) * total)
        sigmas.append(sigma)

    # calculate intervals
    x = []
    y = []
    for i in range(n):
        xi = flow[i] - (alpha * sigmas[i])
        x.append(round(xi, decimal_place))
        yi = flow[i] + (alpha * sigmas[i])
        y.append(round(yi, decimal_place))

    intervals = {"x": x, "y": y}

    return [x, y], pd.DataFrame(intervals, index=alternatives)
