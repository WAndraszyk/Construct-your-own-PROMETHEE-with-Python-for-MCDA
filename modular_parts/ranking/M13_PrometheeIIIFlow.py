import pandas as pd

from core.aliases import FlowsTable, PreferencesTable, NumericValue
import numpy as np


class PrometheeIIIFlow:
    """
    This class computes Promethee III intervals and ranking based on positive and negative flows,
    and preferences.
    """

    def __init__(self, flows: FlowsTable, preferences: PreferencesTable):
        """
        :param flows: FlowsTable of both positive and negative outranking flows.
        :param preferences: PreferenceTable of alternatives over alternatives
        """
        self.alternatives = preferences.index
        self.preferences = preferences
        self.flow = np.subtract(flows['positive'].values, flows['negative'].values)

    def calculate_ranking(self, alpha: NumericValue) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Calculates intervals and outranking pairs:
        1st alternative in pair | relation between variants | 2nd alternative in pair.
        Relationship types:
        P - preferred
        I - indifferent

        :param alpha: parameter used in calculating intervals

        :return: Intervals; Preference ranking pairs
        """
        if alpha <= 0:
            raise Exception("Alpha has to be greater than 0")
        intervals_list, intervals = self.__calculate_intervals__(alpha)
        pairs_data = np.zeros(np.shape(self.preferences), dtype=str)
        for num_a in range(len(self.alternatives)):
            for num_b in range(len(self.alternatives)):
                if intervals_list[0][num_a] > intervals_list[1][num_b]:
                    pairs_data[num_a][num_b] = 'P'
                elif intervals_list[0][num_a] <= intervals_list[1][num_b] \
                        and intervals_list[0][num_b] <= intervals_list[1][num_a]:
                    pairs_data[num_a][num_b] = 'I'
                else:
                    pairs_data[num_a][num_b] = '?'

        pairs = pd.DataFrame(data=pairs_data, columns=self.alternatives, index=self.alternatives)

        return intervals, pairs

    def __calculate_intervals__(self, alpha: NumericValue):
        """
        Calculates intervals used in alternatives comparison.

        :param alpha: parameter used in calculating intervals

        :return: intervals in a list, intervals as a DataFrame
        """
        sigmas = []
        n = len(self.alternatives)
        for i in self.preferences.index:
            total = 0
            for j in self.preferences.columns:
                total += np.square(self.preferences.loc[i, j] - self.preferences.loc[j, i] - self.flow[i])
            sigma = np.sqrt((1 / n) * total)
            sigmas.append(sigma)

        x = []
        y = []
        for i in range(n):
            xi = self.flow[i] - alpha * sigmas[i]
            x.append(xi)
            yi = self.flow[i] + alpha * sigmas[i]
            y.append(yi)

        intervals = {'x': x, 'y': y}

        return [x, y], pd.DataFrame(intervals, index=self.alternatives)
