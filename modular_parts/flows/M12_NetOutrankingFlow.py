import pandas as pd
from pandas import DataFrame

from core.aliases import FlowsTable, NetOutrankingFlows

__all__ = ['calculate_net_outranking_flows', 'calculate_net_outranking_flows_for_prometheeII']


def calculate_net_outranking_flows(flows: FlowsTable) -> NetOutrankingFlows:
    """
    Computes net outranking flow based on positive and negative flows.
    'Net outranking flow' is a difference between positive and negative flow for each alternative.
    :param flows: FlowsTable of both positive and negative outranking flows.
    :return: net outranking flow Series.
    """
    positive_flow = flows['positive'].values
    negative_flow = flows['negative'].values
    alternatives = flows.index
    flow_data = []
    for num_a, alternative_a in enumerate(positive_flow):
        flow_data.append(positive_flow[num_a] - negative_flow[num_a])
    return pd.Series(data=flow_data, index=alternatives, name='Net outranking flow')

def calculate_net_outranking_flows_for_prometheeII(flows: FlowsTable) -> DataFrame:
    """
    Computes net outranking flow based on positive and negative flows.
    'Net outranking flow' is a difference between positive and negative flow for each alternative.

    :param flows: FlowsTable of both positive and negative outranking flows.
    :return: net outranking flow Series.
    """
    flows_copy = flows.copy()
    flows_copy['net'] = calculate_net_outranking_flows(flows).values
    return flows_copy
