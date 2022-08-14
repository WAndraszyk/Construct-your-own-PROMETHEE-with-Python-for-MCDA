
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

    def __calculate_partial_discordance(self, partial_preferences):
        partial_discordance = []
        for n in range(self.k):
            pd_criterion = []
            for j in range(len(partial_preferences[n])):
                pdj = []
                for i in range(len(partial_preferences[n][j])):
                    pdj.append(partial_preferences[n][i][j])
                pd_criterion.append(pdj)
            partial_discordance.append(pd_criterion)

        return partial_discordance

    def __overall_discordance(self, partial_discordance, tau):
        discordance = []
        for i in range(len(partial_discordance[0])):
            aggregated_discordance = []
            for j in range(len(partial_discordance[0][0])):
                D_a_b = 0
                for n in range(self.k):
                    D_a_b += pow(1 - partial_discordance[n][i][j], tau / self.k)
                D_a_b = 1 - D_a_b
                aggregated_discordance.append(D_a_b)
            discordance.append(aggregated_discordance)

        return discordance

    def calculate_discordance(self, tau, calculate_preference=False):
        if tau < 1 or tau > len(self.k):
            raise Exception("Tau needs to be a number from 1 to k, where k is the number of criteria.")

        if not self.categories_profiles:
            partial_discordance = self.__calculate_partial_discordance(self.partial_preferences)
            discordance = self.__overall_discordance(partial_discordance, tau)
        else:
            partial_discordance = []
            for i in self.partial_preferences:
                partial_discordance.append(self.__calculate_partial_discordance(i))
            discordance = []
            for i in partial_discordance:
                discordance.append(self.__overall_discordance(i, tau))

        if calculate_preference:
            return 0  # TODO: obliczanie preferencji z M8
        else:
            return discordance, partial_discordance
