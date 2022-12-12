"""
    This module computes net outranking flows based on positive and negative
    outranking flows.
"""
from typing import Union

import pandas as pd

__all__ = ['calculate_net_outranking_flows']

from core.input_validation import calculate_net_outranking_flows_validation


def calculate_net_outranking_flows(flows: pd.DataFrame,
                                   promethee_II_format: bool = False) \
        -> Union[pd.Series, pd.DataFrame]:
    """
    Computes net outranking flow based on positive and negative flows.
    'Net outranking flow' is a difference between positive and negative flow
    for each alternative.

    :param flows: FlowsTable of both positive and negative outranking flows.
    :param promethee_II_format: boolean value describe whether net flow should
        be return alone or as DataFrame together with outranking flows

    :return: Series of net outranking flow or DataFrame of
        outranking flows wit net outranking flow
    """

    calculate_net_outranking_flows_validation(flows)
    positive_flow = flows['positive'].values
    negative_flow = flows['negative'].values
    alternatives = flows.index
    flow_data = []
    for num_a, alternative_a in enumerate(positive_flow):
        flow_data.append(positive_flow[num_a] - negative_flow[num_a])

    net = pd.Series(data=flow_data, index=alternatives,
                    name='Net outranking flow')
    if promethee_II_format:
        net_flow = flows.copy()
        net_flow['net'] = net
        return net_flow
    else:
        return net

