import pandas as pd
import numpy as np
from core.aliases import DMsTable


class PrometheeGroupRanking:
    """
    This class calculates aggregated flows which are weighted sum of flows for every alternative.
    Allows many Decision Makers to get influence on final flows.
    """

    def __init__(self, dms_data: DMsTable):
        """
        :param dms_data: DMsTable of DMs flows (positive or negative) and weights values.
        """
        self.dms_data = dms_data.T

    def __calculate_weighted_flows(self) -> np.ndarray:
        """
        Calculates weighted flows by multiplying flows by each DM weight.
        :return: ndarray(2 dim) of weighted flows
        """
        return np.multiply(self.dms_data['weights'], self.dms_data[self.dms_data.columns.difference(['weights'])].T).T

    def calculate_group_ranking(self) -> pd.DataFrame:
        """
        Calculates aggregated flows.
        :return: DataFrame with aggregated flows(column 'aggregated') and  weighted flows(column 'weighted')
        """
        alternatives = self.dms_data.index
        weighted_flows = self.__calculate_weighted_flows()
        aggregated_flows = np.sum(weighted_flows, axis=0)

        return pd.DataFrame([weighted_flows, aggregated_flows], columns=['weighted', 'aggregated'], index=alternatives)


