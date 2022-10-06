import copy
import pandas as pd
from typing import List
from core.aliases import NumericValue
from core.preference_commons import overall_preference


class PrometheeDiscordance:
    def __init__(self, criteria: List[str], partial_preferences: pd.DataFrame, categories_profiles=False):
        """
        :param partial_preferences: partial preference of every alternative over other alternatives
        or profiles
        :param categories_profiles: were the preferences calculated for profiles
        """

        self.alternatives = partial_preferences.keys()
        self.criteria = criteria
        self.categories_profiles = categories_profiles
        self.partial_preferences = partial_preferences

    def __calculate_partial_discordance(self, partial_preferences, other_partial_preferences=None):
        """
        Calculates partial discordance indices based on partial preference indices

        :param partial_preferences: partial preference of every alternative over other alternatives
        or profiles
        :return: 3D matrix of partial discordance indices
        """
        partial_discordance = partial_preferences.copy(deep=True)
        if other_partial_preferences is None:
            other_partial_preferences = partial_preferences
        for criterion in self.criteria:
            for j in partial_preferences.keys():
                for i in other_partial_preferences.columns:
                    partial_discordance.loc[criterion, j][i] = other_partial_preferences.loc[criterion, i][j]

        return partial_discordance

    def __overall_discordance(self, partial_discordance, tau):
        """
        Calculates overall discordance by aggregating partial discordance indices.

        :param partial_discordance: matrix of partial discordance indices
        :param tau: technical parameter, τ ∈ [1, k], smaller τ → weaker discordance
        :return: matrix of overall discordance
        """
        discordance = []
        k = len(self.criteria)
        index = partial_discordance.loc[self.criteria[0]].index
        columns = partial_discordance.loc[self.criteria[0]].columns
        for i in index:
            aggregated_discordance = []
            for column in columns:
                D_a_b = 1
                for criterion in self.criteria:
                    D_a_b *= pow(1 - partial_discordance.loc[criterion, i][column], tau / k)
                D_a_b = 1 - D_a_b
                aggregated_discordance.append(D_a_b)
            discordance.append(aggregated_discordance)

        return pd.DataFrame(data=discordance, index=index, columns=columns)

    def compute_discordance(self, tau: NumericValue, preferences=None):
        """
        Calculates overall discordance by aggregating partial discordance indices.

        :param tau: technical parameter, τ ∈ [1, k], smaller τ → weaker discordance
        :param preferences: if not empty function returns already calculated preference instead of just discordance
        :return: matrix of overall discordance and matrix of partial discordance indices. Alternatively: preference
        """
        if tau < 1 or tau > len(self.criteria):
            raise Exception("Tau needs to be a number from 1 to k, where k is the number of criteria.")

        if not self.categories_profiles:
            partial_discordance = self.__calculate_partial_discordance(self.partial_preferences)
            discordance = self.__overall_discordance(partial_discordance, tau)
        else:
            partial_discordance = [
                self.__calculate_partial_discordance(self.partial_preferences[0], self.partial_preferences[1]),
                self.__calculate_partial_discordance(self.partial_preferences[1], self.partial_preferences[0])]
            discordance = []
            for i in partial_discordance:
                discordance.append(self.__overall_discordance(i, tau))

        if preferences is not None:
            return overall_preference(preferences, discordance, self.categories_profiles)
        else:
            return discordance, partial_discordance
