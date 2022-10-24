from core.preference_commons import PreferenceFunction
from core.aliases import NumericValue, PerformanceTable
from typing import List
import core.generalized_criteria as gc
import core.preference_commons as pc
import pandas as pd


class PrometheePreferenceReinforcedPreference:
    def __init__(self,
                 alternatives_performances: PerformanceTable,
                 preference_thresholds: pd.Series,
                 indifference_thresholds: pd.Series,
                 generalized_criteria: pd.Series,
                 directions: pd.Series,
                 reinforced_preference_thresholds: pd.Series,
                 reinforcement_factors: pd.Series,
                 weights: pd.Series,
                 profiles_performance: PerformanceTable = None,
                 decimal_place: NumericValue = 3):
        """
        :param alternatives_performances: Dataframe of alternatives' value at every criterion
        :param weights: criteria with weights
        :param generalized_criteria: method used for computing partial preference indices
        :param preference_thresholds: preference threshold for each criterion
        :param indifference_thresholds: indifference threshold for each criterion
        :param generalized_criteria: list of preference functions
        :param directions: directions of preference of criteria
        :param reinforced_preference_thresholds: list of reinforced preference threshold for each criterion
        :param reinforcement_factors: list of reinforcement factor for each criterion
        :param weights: criteria with weights
        :param profiles_performance: Dataframe of profiles performance (value) at every criterion
        :param decimal_place: with this you can choose the decimal_place of the output numbers
        """
        self.alternatives = alternatives_performances.index
        self.criteria = weights.keys()
        self.alternatives_performances = pc.directed_alternatives_performances(alternatives_performances, directions)
        self.weights = weights
        self.generalized_criteria = generalized_criteria
        self.preference_thresholds = preference_thresholds
        self.indifference_thresholds = indifference_thresholds
        self.reinforced_preference_thresholds = reinforced_preference_thresholds
        self.reinforcement_factors = reinforcement_factors
        if profiles_performance is not None:
            self.categories_profiles = profiles_performance.keys()
            self.profile_performance_table = pc.directed_alternatives_performances(profiles_performance, directions)
        else:
            self.categories_profiles = None
            self.profile_performance_table = None
        self.decimal_place = decimal_place
        self.Frp = []

    def computePreferenceIndices(self):
        """
        Calculates preference of every alternative over other alternatives
        or profiles based on partial preferences.
        Includes reinforced preference effect.

        :return: preferences
        :return: partial preferences
        """
        partialPref = self.__partialPreference()
        if self.categories_profiles is None:
            return self.__preferences(partialPref, self.Frp, self.alternatives_performances), partialPref
        else:
            return (self.__preferences(partialPref[0], self.Frp[0], self.alternatives_performances,
                                       self.profile_performance_table),
                    self.__preferences(partialPref[1], self.Frp[1], self.profile_performance_table,
                                       self.alternatives_performances)), partialPref

    def __partialPreference(self):
        """
        Calculates partial preference of every alternative over others at every criterion
        based on deviations using a method chosen by user. If deviation is greater then
        reinforced preference threshold than partial preference takes the value of
        reinforcement factor.
        :return: partial preference indices
        """
        deviations = pc.deviations(self.criteria, self.alternatives_performances, self.profile_performance_table)
        if self.categories_profiles is None:
            ppIndices, self.Frp = self.__pp_deep(deviations, self.alternatives_performances,
                                                 self.alternatives_performances)
        else:

            ppIndices0, Frp0 = self.__pp_deep(deviations[0], self.alternatives_performances,
                                              self.profile_performance_table)
            ppIndices1, Frp1 = self.__pp_deep(deviations[1], self.profile_performance_table,
                                              self.alternatives_performances)
            ppIndices = [ppIndices0, ppIndices1]
            self.Frp = [Frp0, Frp1]

        return ppIndices

    def __pp_deep(self, deviations, i_iter, j_iter):
        ppIndices = []
        FrpList = []
        for k in range(len(self.criteria)):
            method = self.generalized_criteria[k]
            q = self.indifference_thresholds[k]
            p = self.preference_thresholds[k]
            criterionIndices = []
            criterionFrp = []
            for i in range(i_iter.shape[0]):
                alternativeIndices = []
                alternativeFrp = []
                for j in range(j_iter.shape[0]):
                    if deviations[k][i][j] > self.reinforced_preference_thresholds[self.criteria[k]]:
                        alternativeIndex = self.reinforcement_factors[self.criteria[k]]
                        Frp = 1
                    else:
                        Frp = 0
                        if method is PreferenceFunction.USUAL:
                            alternativeIndex = gc.usual_criterion(deviations[k][i][j])
                        elif method is PreferenceFunction.U_SHAPE:
                            alternativeIndex = gc.u_shape_criterion(deviations[k][i][j], q)
                        elif method is PreferenceFunction.V_SHAPE:
                            alternativeIndex = gc.v_shape_criterion(deviations[k][i][j], p)
                        elif method is PreferenceFunction.LEVEL:
                            if q > p:
                                raise ValueError(
                                    "incorrect threshold : q "
                                    + str(q)
                                    + " greater than p "
                                    + str(p)
                                )
                            alternativeIndex = gc.level_criterion(deviations[k][i][j], p, q)
                        elif method is PreferenceFunction.V_SHAPE_INDIFFERENCE:
                            if q > p:
                                raise ValueError(
                                    "incorrect threshold : q "
                                    + str(q)
                                    + " greater than p "
                                    + str(p)
                                )
                            alternativeIndex = gc.v_shape_indifference_criterion(deviations[k][i][j], p, q)
                        else:
                            raise ValueError(
                                "pref_func "
                                + str(method)
                                + " is not known or forbidden."
                            )
                    alternativeIndices.append(alternativeIndex)
                    alternativeFrp.append(Frp)
                criterionIndices.append(alternativeIndices)
                criterionFrp.append(alternativeFrp)
            ppIndices.append(criterionIndices)
            FrpList.append(criterionFrp)

        names = ['criteria'] + i_iter.index.names
        ppIndices = pd.concat([pd.DataFrame(data=x, index=i_iter.index, columns=j_iter.index) for x in ppIndices],
                              keys=self.criteria,
                              names=names)

        return ppIndices, FrpList

    def __preferences(self, partialPref, Frp, i_perf, j_perf=None):
        i_iter = i_perf.index
        if j_perf is None:
            j_iter = i_iter
        else:
            j_iter = j_perf.index
        preferences = []
        for i in range(len(i_iter)):
            aggregatedPI = []
            for j in range(len(j_iter)):
                Pi_A_B_nom = 0
                Pi_A_B_denom = 0
                for k in range(len(self.criteria)):
                    Pi_A_B_nom += partialPref.loc[self.criteria[k], i_iter[i]][j_iter[j]] * self.weights[self.criteria[k]]
                    if Frp[k][i][j] == 1:
                        Pi_A_B_denom += self.weights[self.criteria[k]] * self.reinforcement_factors[self.criteria[k]]
                    else:
                        Pi_A_B_denom += self.weights[self.criteria[k]]
                Pi_A_B = round(Pi_A_B_nom / Pi_A_B_denom, self.decimal_place)
                aggregatedPI.append(Pi_A_B)
            preferences.append(aggregatedPI)

        preferences = pd.DataFrame(data=preferences, columns=j_iter, index=i_iter)
        return preferences
