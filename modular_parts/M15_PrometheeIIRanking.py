"""
.. image:: prometheePUT_figures/M15.jpg

This module creates a Promethee II ranking based on flows calculated with
Promethee II method.

Implementation and naming of conventions are taken from
:cite:p:`BransMareschal2005`.
"""
from typing import Union

import pandas as pd

from core.input_validation.ranking import promethee_ii_ranking_validation

__all__ = ["calculate_promethee_ii_ranking"]


def calculate_promethee_ii_ranking(
    promethee_ii_flows: Union[pd.DataFrame, pd.Series],
) -> pd.Series:
    """
    Creates a Promethee II ranking.

    :param promethee_ii_flows: DataFrame of Promethee II flows(net flows)
        flows as values, alternatives as index and flow types as columns or
        Series with alternatives as index and flows as values

    :return: Series representing Promethee II ranking
    """
    # input data validation
    promethee_ii_ranking_validation(promethee_ii_flows)

    if isinstance(promethee_ii_flows, pd.DataFrame):
        # create ranking based on net flows
        data = promethee_ii_flows.sort_values("net", ascending=False).index
        ranking = pd.Series(data=data, name="ranking")
        # start indexing from 1
        ranking.index += 1
        return ranking
    else:
        # create ranking based on flows
        data = promethee_ii_flows.sort_values(ascending=False).index
        ranking = pd.Series(data=data, name="ranking")
        # start indexing from 1
        ranking.index += 1
        return ranking
