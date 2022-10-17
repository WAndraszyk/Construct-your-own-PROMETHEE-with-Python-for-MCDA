from enum import Enum
from core.aliases import NumericValue, PerformanceTable
from typing import List
import core.preference_commons as pc
import pandas as pd


class PrometheeVeto:
    """
    This class computes aggregated veto indices and partial veto indices.
    """

    def __init__(self,
                 alternatives_performances: PerformanceTable,
                 weights: pd.Series,
                 v_list: pd.Series,
                 directions: pd.Series,
                 profiles_performance: PerformanceTable = None,
                 decimal_place: NumericValue = 3,
                 full_veto: bool = True):
        """
        :param alternatives_performances: Dataframe of alternatives' value at every criterion
        :param weights: criteria with weights
        :param v_list: veto threshold for each criteria
        :param directions: directions of preference of criteria
        :param profiles_performance: Dataframe of profiles performance (value) at every criterion
        :param decimal_place: with this you can choose the decimal_place of the output numbers
        :param full_veto: choose methode of calculating vetoes
        """
        self.alternatives = alternatives_performances.index
        self.criteria = weights.keys()
        self.alternatives_performances = pc.directed_alternatives_performances(alternatives_performances, directions)
        self.weights = weights
        self.v_list = v_list
        self.decimal_place = decimal_place
        self.full_vet = full_veto
        if profiles_performance is not None:
            self.categories_profiles = profiles_performance.keys()
            self.profile_performance_table = pc.directed_alternatives_performances(profiles_performance, directions)
        else:
            self.categories_profiles = None
            self.profile_performance_table = None

    def __veto_deep(self, deviations, i_iter, j_iter):
        pvetos = []
        for k in range(self.criteria.size):
            v = self.v_list[k]
            criterionIndices = []
            for j in range(i_iter.shape[0]):
                alternative_Vetoes = []
                for i in range(j_iter.shape[0]):
                    if v is None:
                        alternative_Vetoes.append(0)
                    elif deviations[k][i][j] >= v:
                        alternative_Vetoes.append(1)
                    else:
                        alternative_Vetoes.append(0)
                criterionIndices.append(alternative_Vetoes)
            pvetos.append(criterionIndices)

        names = ['criteria'] + i_iter.index.names
        pvetos = pd.concat([pd.DataFrame(data=x, index=i_iter.index, columns=j_iter.index) for x in pvetos],
                           keys=self.criteria,
                           names=names)
        return pvetos

    def __partial_veto(self) -> List[List[List[NumericValue]]]:
        """
        Calculates partial veto of every alternative over other alternatives
        or profiles at every criterion based on deviations using a method chosen by user.

        :return: partial veto
        """
        deviations = pc.deviations(criteria=self.criteria, alternatives_performances=self.alternatives_performances,
                                   profile_performance_table=self.profile_performance_table)
        if not self.categories_profiles:

            pvetos = self.__veto_deep(deviations=deviations, i_iter=self.alternatives_performances,
                                      j_iter=self.alternatives_performances)
        else:
            pvetos = [
                self.__veto_deep(deviations=deviations[0], i_iter=self.alternatives_performances,
                                 j_iter=self.profile_performance_table),
                self.__veto_deep(deviations=deviations[1], i_iter=self.profile_performance_table,
                                 j_iter=self.alternatives_performances)]
        return pvetos

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
            veto = self.__vetoes(partial_veto=partialVet, i_iter=self.alternatives)
            partial_veto = partialVet
        else:
            partial_veto = partialVet[1], partialVet[0]
            veto = (self.__vetoes(partial_veto=partialVet[1], i_iter=self.categories_profiles,
                                  j_iter=self.alternatives),
                    self.__vetoes(partial_veto=partialVet[0], i_iter=self.alternatives,
                                  j_iter=self.categories_profiles))
        if preferences is not None:
            return pc.overall_preference(preferences, veto, self.categories_profiles)
        else:
            return veto, partial_veto


    def __vetoes(self, partial_veto, i_iter, j_iter=None):
        if j_iter is None:
            j_iter = i_iter
        Vetoes = []
        index = partial_veto.loc[self.criteria[0]].index
        columns = partial_veto.loc[self.criteria[0]].columns
        for j in j_iter:
            aggregated_v = []
            for i in i_iter:
                Pi_A_B = 0
                for k in self.criteria:
                    if self.full_vet:
                        if partial_veto.loc[k,j][i] == 1:
                            Pi_A_B = 1
                            break
                    else:
                        Pi_A_B += partial_veto.loc[k,j][i] * self.weights[k]

                aggregated_v.append(Pi_A_B)
            Vetoes.append(aggregated_v)

        return pd.DataFrame(data=Vetoes, index=index, columns=columns)
