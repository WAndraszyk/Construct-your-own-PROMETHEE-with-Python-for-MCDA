from core.aliases import NumericValue
from typing import List
import core.preference_commons as pc


class PrometheeVeto:
    def __init__(self,
                 criteria,
                 alternatives_performances: List[List[NumericValue]],
                 weights: List[NumericValue],
                 v_list: List[NumericValue],
                 directions: List[NumericValue],
                 categories_profiles: bool = False,
                 profile_performance_table: List[List[NumericValue]] = None,
                 decimal_place: NumericValue = 3,
                 full_veto: bool = True):
        """
        :param criteria: list of criteria
        :param alternatives_performances: 2D list of alternatives' value at every criterion
        :param weights: list of weights
        :param v_list: list of veto threshold for each criteria
        :param directions: directions of Veto of criteria
        :param categories_profiles: boolean value, when vetoes are calculated for profiles
        :param profile_performance_table: 2D list of profiles performance (value) at every criterion
        :param decimal_place: with this you can choose the decimal_place of the output numbers
        :param full_veto: choose methode of calculating vetoes
        """

        self.criteria = criteria
        self.alternatives_performances = pc.directed_alternatives_performances(alternatives_performances, directions)
        self.weights = weights
        self.v_list = v_list
        self.v_list = v_list
        self.decimal_place = decimal_place
        self.categories_profiles = categories_profiles
        self.full_vet = full_veto
        if profile_performance_table is not None:
            self.profile_performance_table = pc.directed_alternatives_performances(profile_performance_table,
                                                                                   directions)
        else:
            self.profile_performance_table = profile_performance_table

    def __veto_deep(self, deviations, i_iter, j_iter):
        ppIndices = []
        for k in range(len(self.criteria)):
            v = self.v_list[k]
            criterionIndices = []
            for j in range(len(j_iter)):
                alternative_Vetoes = []
                for i in range(len(i_iter)):
                    if deviations[k][i][j] >= v:
                        alternative_Vetoes.append(1)
                    else:
                        alternative_Vetoes.append(0)
                criterionIndices.append(alternative_Vetoes)
            ppIndices.append(criterionIndices)
        return ppIndices

    def __partial_veto(self) -> List[List[List[NumericValue]]]:
        """
        Calculates partial veto of every alternative over other alternatives
        or profiles at every criterion based on deviations using a method chosen by user.

        :return: partial veto
        """
        deviations = pc.deviations(self.criteria, self.alternatives_performances, self.profile_performance_table)
        if not self.categories_profiles:

            ppIndices = self.__veto_deep(deviations, self.alternatives_performances, self.alternatives_performances)
        else:
            ppIndices = [
                self.__veto_deep(deviations[0], self.alternatives_performances, self.profile_performance_table),
                self.__veto_deep(deviations[1], self.profile_performance_table, self.alternatives_performances)]
        return ppIndices

    def compute_veto(self, preferences=None):
        """
        Calculates veto of every alternative over other alternatives
        or profiles based on partial veto

        :param preferences: if not None function returns already calculated preference instead of just veto
        :return: veto
        :return: partial veto
        """
        partialVet = self.__partial_veto()

        if not self.categories_profiles:
            veto = self.__vetoes(partialVet, self.alternatives_performances)
            partial_veto = partialVet
        else:
            partial_veto = partialVet[1], partialVet[0]
            veto = (self.__vetoes(partialVet[1], self.profile_performance_table, self.alternatives_performances),
                    self.__vetoes(partialVet[0], self.alternatives_performances, self.profile_performance_table))
        if preferences is not None:
            return pc.overall_preference(preferences, veto, self.categories_profiles)
        else:
            return veto, partial_veto

    def __vetoes(self, partialVet, i_iter, j_iter=None):
        if j_iter is None:
            j_iter = i_iter
        Vetoes = []
        for j in range(len(j_iter)):
            aggregatedPI = []
            for i in range(len(i_iter)):
                Pi_A_B = 0
                for k in range(len(self.criteria)):
                    if self.full_vet:
                        if partialVet[k][j][i] == 1:
                            Pi_A_B = 1
                            break
                    else:
                        Pi_A_B += partialVet[k][j][i] * self.weights[k]

                aggregatedPI.append(Pi_A_B)
            Vetoes.append(aggregatedPI)

        return Vetoes
