import pandas as pd
from core.aliases import PerformanceTable, PreferencesTable, FlowsTable
from typing import Tuple, Union


class PrometheeOutrankingFlows:
    """
    This class computes positive and negative outranking flows
    based on preferences.
    """

    def __init__(self, preferences: Union[Tuple[PreferencesTable, PreferencesTable], PreferencesTable],
                 category_profiles: PerformanceTable = None):
        # Rozkminic czy zamiast tupla nie wrzucac drugiego df jako category_profiles

        """
        :param preferences: PreferenceTable of aggregated preferences (profile over profile ) or 2-element
        tuple of PreferenceTables of aggregated preferences (profile over category and category over profile).
        :param category_profiles: PreferenceTable of category profiles.
        """
        self.category_profiles = category_profiles
        self.preferences = preferences

    def __calculate_flow(self, positive: bool = True) -> pd.Series:
        """
        Calculate positive or negative outranking flow.

        :param positive: If True function returns positive outranking flow
                         else returns negative outranking flow.
        :return: List of outranking flow's values.
        """
        if isinstance(self.preferences, tuple):
            if positive:
                flows = self.preferences[0].mean(axis=1)
            else:
                flows = self.preferences[1].mean(axis=0)
        else:
            n = self.preferences.shape[0]

            axis = 1 if positive else 0
            aggregated_preferences = self.preferences.sum(axis=axis)
            flows = aggregated_preferences / (n - 1)

        return flows

    def calculate_flows(self) -> FlowsTable:
        """
        Calculate both positive and negative outranking flows.

        :return: FlowTable of both positive and negative outranking flows.
        """
        index = self.preferences[0].index if isinstance(self.preferences, tuple) else self.preferences.index
        return pd.DataFrame({'positive': self.__calculate_flow(), 'negative': self.__calculate_flow(positive=False)},
                            index=index)
