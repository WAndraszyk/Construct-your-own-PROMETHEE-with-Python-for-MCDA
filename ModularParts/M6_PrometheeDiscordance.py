import copy
from core.preference_commons import overall_preference


class PrometheeDiscordance:
    def __init__(self, k, partial_preferences, categories_profiles=False):
        """
        :param k: number of criteria
        :param partial_preferences: partial preference of every alternative over other alternatives
        or profiles
        :param categories_profiles: were the preferences calculated for profiles
        """

        self.k = k
        self.categories_profiles = categories_profiles
        self.partial_preferences = partial_preferences

    def __calculate_partial_discordance(self, partial_preferences, other_partial_preferences=None):
        """
        Calculates partial discordance indices based on partial preference indices

        :param partial_preferences: partial preference of every alternative over other alternatives
        or profiles
        :return: 3D matrix of partial discordance indices
        """
        partial_discordance = copy.deepcopy(partial_preferences)
        if other_partial_preferences is None:
            other_partial_preferences = partial_preferences
        for n in range(self.k):
            for j in range(len(partial_preferences[n])):
                for i in range(len(partial_preferences[n][j])):
                    partial_discordance[n][j][i] = other_partial_preferences[n][i][j]

        return partial_discordance

    def __overall_discordance(self, partial_discordance, tau):
        """
        Calculates overall discordance by aggregating partial discordance indices.

        :param partial_discordance: matrix of partial discordance indices
        :param tau: technical parameter, τ ∈ [1, k], smaller τ → weaker discordance
        :return: matrix of overall discordance
        """
        discordance = []
        for i in range(len(partial_discordance[0])):
            aggregated_discordance = []
            for j in range(len(partial_discordance[0][0])):
                D_a_b = 1
                for n in range(self.k):
                    D_a_b *= pow(1 - partial_discordance[n][i][j], tau / self.k)
                D_a_b = 1 - D_a_b
                aggregated_discordance.append(D_a_b)
            discordance.append(aggregated_discordance)

        return discordance

    def compute_discordance(self, tau, preferences=None):
        """
        Calculates overall discordance by aggregating partial discordance indices.

        :param tau: technical parameter, τ ∈ [1, k], smaller τ → weaker discordance
        :param preferences: if not empty function returns already calculated preference instead of just discordance
        :return: matrix of overall discordance and matrix of partial discordance indices. Alternatively: preference
        """
        if tau < 1 or tau > self.k:
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
