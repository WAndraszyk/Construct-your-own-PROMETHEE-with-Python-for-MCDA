from core.preference_commons import PreferenceFunction
from core.aliases import NumericValue
from typing import List
import core.generalized_criteria as gc
import core.preference_commons as pc


class PrometheePreferenceReinforcedPreference:
    def __init__(self,
                 alternatives,
                 criteria,
                 alternatives_performances: List[List[NumericValue]],
                 weights: List[NumericValue],
                 p_list: List[NumericValue],
                 q_list: List[NumericValue],
                 generalized_criteria,
                 directions: List[NumericValue],
                 rp_list: List[NumericValue],
                 omega_list: List[NumericValue],
                 categories_profiles: List[str] = None,
                 profile_performance_table: List[List[NumericValue]] = None,
                 decimal_place: NumericValue = 3):
        """
        :param alternatives: list of alternatives (rozumiemy to jako liste samych nazw)
        :param criteria: list of criteria
        :param alternatives_performances: 2D list of alternatives' value at every criterion
        :param weights: list of weights
        :param generalized_criteria: method used for computing partial preference indices
        :param p_list: list of preference threshold for each criterion
        :param q_list: list of indifference threshold for each criterion
        :param generalized_criteria: list of preference functions
        :param directions: directions of preference of criteria
        :param rp_list: list of reinforced preference threshold for each criterion
        :param omega_list: list of reinforcement factor for each criterion
        :param categories_profiles: list of profiles (names, strings)
        :param profile_performance_table: 2D list of profiles performance (value) at every criterion
        :param decimal_place: with this you can choose the decimal_place of the output numbers
        """
        self.alternatives = alternatives
        self.criteria = criteria
        self.alternatives_performances = pc.directed_alternatives_performances(alternatives_performances, directions)
        self.weights = weights
        self.generalized_criteria = generalized_criteria
        self.p_list = p_list
        self.q_list = q_list
        self.rp_list = rp_list
        self.omega_list = omega_list
        self.categories_profiles = categories_profiles
        if profile_performance_table is not None:
            self.profile_performance_table = pc.directed_alternatives_performances(profile_performance_table,
                                                                                   directions)
        else:
            self.profile_performance_table = profile_performance_table
        self.decimal_place = decimal_place
        self.Frp = []

    def __pp_deep(self, deviations, i_iter, j_iter):
        ppIndices = []
        FrpList = []
        for k in range(len(self.criteria)):
            method = self.generalized_criteria[k]
            q = self.q_list[k]
            p = self.p_list[k]
            criterionIndices = []
            criterionFrp = []
            for i in range(len(i_iter)):
                alternativeIndices = []
                alternativeFrp = []
                for j in range(len(j_iter)):
                    if deviations[k][i][j] > self.rp_list[k]:
                        alternativeIndex = self.omega_list[k]
                        Frp = 1
                    else:
                        Frp = 0
                        if method is PreferenceFunction.USUAL:
                            alternativeIndex = gc.usualCriterion(deviations[k][i][j])
                        elif method is PreferenceFunction.U_SHAPE:
                            alternativeIndex = gc.uShapeCriterion(deviations[k][i][j], q)
                        elif method is PreferenceFunction.V_SHAPE:
                            alternativeIndex = gc.vShapeCriterion(deviations[k][i][j], p)
                        elif method is PreferenceFunction.LEVEL:
                            if q > p:
                                raise ValueError(
                                    "incorrect threshold : q "
                                    + str(q)
                                    + " greater than p "
                                    + str(p)
                                )
                            alternativeIndex = gc.levelCriterion(deviations[k][i][j], p, q)
                        elif method is PreferenceFunction.V_SHAPE_INDIFFERENCE:
                            if q > p:
                                raise ValueError(
                                    "incorrect threshold : q "
                                    + str(q)
                                    + " greater than p "
                                    + str(p)
                                )
                            alternativeIndex = gc.vShapeIndifferenceCriterion(deviations[k][i][j], p, q)
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

        return ppIndices, FrpList

    def __partialPreference(self) -> List[List[List[NumericValue]]]:
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

    def __preferences(self, partialPref, Frp, i_iter, j_iter=None):
        if j_iter is None:
            j_iter = i_iter
        preferences = []
        for i in range(len(i_iter)):
            aggregatedPI = []
            for j in range(len(j_iter)):
                Pi_A_B_nom = 0
                Pi_A_B_denom = 0
                for k in range(len(self.criteria)):
                    Pi_A_B_nom += partialPref[k][i][j] * self.weights[k]
                    if Frp[k][i][j] == 1:
                        Pi_A_B_denom += self.weights[k] * self.omega_list[k]
                    else:
                        Pi_A_B_denom += self.weights[k]
                Pi_A_B = round(Pi_A_B_nom / Pi_A_B_denom, self.decimal_place)
                aggregatedPI.append(Pi_A_B)
            preferences.append(aggregatedPI)

        return preferences
