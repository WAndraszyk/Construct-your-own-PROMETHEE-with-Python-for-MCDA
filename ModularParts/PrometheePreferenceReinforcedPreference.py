from enum import Enum
from core.aliases import NumericValue
from typing import List
import core.generalized_criteria as gc
import core.preference_commons as pc


class PreferenceFunction(Enum):
    """Enumeration of the preference functions."""

    USUAL = 1
    U_SHAPE = 2
    V_SHAPE = 3
    LEVEL = 4
    V_SHAPE_INDIFFERENCE = 5


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
                 decimal_place: NumericValue = 3):
        """
        Nie uwzględniono boundary profiles oraz characteristic profiles.

        :param alternatives: list of alternatives (rozumiemy to jako liste samych nazw)
        :param criteria: list of criteria
        :param alternatives_performances: 2D list of alternatives' value at every criterion
        :param weights: list of weights
        :param generalized_criteria: method used for computing partial preference indices
        :param decimal_place: with this you can choose the decimal_place of the output numbers
        :param p_list: list of preference threshold for each criterion
        :param q_list: list of indifference threshold for each criterion
        :param generalized_criteria: list of preference functions
        :param directions: directions of preference of criteria
        :param rp_list: list of reinforced preference threshold for each criterion
        :param omega_list: list of reinforcement factor for each criterion
        """
        self.alternatives = alternatives
        self.criteria = criteria
        self.alternatives_performances = pc.directed_alternatives_performances(alternatives_performances, directions)
        self.weights = weights
        self.decimal_place = decimal_place
        self.generalized_criteria = generalized_criteria
        self.p_list = p_list
        self.q_list = q_list
        self.rp_list = rp_list
        self.omega_list = omega_list
        self.Frp = []

    def __partialPreference(self) -> List[List[List[NumericValue]]]:
        """
        Calculates partial preference of every alternative over others at every criterion
        based on deviations using a method chosen by user. If deviation is greater then
        reinforced preference threshold than partial preference takes the value of
        reinforcement factor.

        :return: partial preference indices
        """
        deviations = pc.deviations(self.criteria, self.alternatives_performances)
        ppIndices = []
        for k in range(len(self.criteria)):
            method = self.generalized_criteria[k]
            q = self.q_list[k]
            p = self.p_list[k]
            criterionIndices = []
            criterionFrp = []
            for i in range(len(self.alternatives_performances)):
                alternativeIndices = []
                alternativeFrp = []
                for j in range(len(self.alternatives_performances)):
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
                            alternativeIndex = gc.vShapeCriterion(deviations[k][i][j], p, self.decimal_place)
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
                            alternativeIndex = gc.vShapeIndifferenceCriterion(deviations[k][i][j], p, q,
                                                                                  self.decimal_place)
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
            self.Frp.append(criterionFrp)
        return ppIndices

    def computePreferenceIndices(self):
        """
        Calculates preference of every alternative over others based on partial preferences.
        Includes reinforced preference effect.

        :return: preferences
        :return: partial preferences
        """
        partialPref = self.__partialPreference()
        preferences = []
        for i in range(len(self.alternatives_performances)):
            aggregatedPI = []
            for j in range(len(self.alternatives_performances)):
                Pi_A_B_nom = 0
                Pi_A_B_denom = 0
                for k in range(len(self.criteria)):
                    Pi_A_B_nom += partialPref[k][i][j] * self.weights[k]
                    if self.Frp[k][i][j] == 1:
                        Pi_A_B_denom += self.weights[k] * self.omega_list[k]
                    else:
                        Pi_A_B_denom += self.weights[k]
                Pi_A_B = round(Pi_A_B_nom/Pi_A_B_denom, self.decimal_place)
                aggregatedPI.append(Pi_A_B)
            preferences.append(aggregatedPI)

        return preferences, partialPref
