import pandas as pd

from core.aliases import FlowsTable, NetOutrankingFlows

__all__ = []


class NetOutrankingFlow:
    """
    This class compute net outranking flow for net outranking flow based on positive and negative flows.
    'Net outranking flow' is a difference between positive and negative flow for each alternative.
    """

    def __init__(self, flows: FlowsTable):
        """
        :param flows: FlowsTable of both positive and negative outranking flows.
        """
        self.positive_flow = flows['positive'].values
        self.negative_flow = flows['negative'].values
        self.alternatives = flows.index

    def calculate_net_outranking_flows(self) -> NetOutrankingFlows:
        """
        Calculates net outranking flow.
        :return: net outranking flow Series.
        """
        flow_data = []
        for num_a, alternative_a in enumerate(self.positive_flow):
            flow_data.append(self.positive_flow[num_a] - self.negative_flow[num_a])
        return pd.Series(data=flow_data, index=self.alternatives, name='Net outranking flow')
