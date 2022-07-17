from enum import Enum
from core.aliases import NumericValue
from typing import List
import core.generalized_criteria as gc


class PreferenceFunction(Enum):
    """Enumeration of the preference functions."""

    USUAL = 1
    U_SHAPE = 2
    V_SHAPE = 3
    LEVEL = 4
    V_SHAPE_INDIFFERENCE = 5
    GAUSSIAN = 6


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
                 decimal_place: NumericValue = 3):
        """
        Nie uwzględniono boundary profiles oraz characteristic profiles.
        @param alternatives: list of alternatives (rozumiemy to jako liste samych nazw)
        :param criteria: list of criteria
        :param alternatives_performances: 2D list of alternatives' value at every criterion
        :param weights: list of weights
        :param generalized_criterion: method used for computing partial preference indices
        :param decimal_place: with this you can choose the decimal_place of the output numbers
        :param p_list: list of preference threshold for each criteria
        :param q_list: list of indifference threshold for each criteria
        :param s_list: list of standard deviation for each criteria
        :param generalized_criteria: list of preference functions
        :param directions: directions of preference of criteria


        """
        self.alternatives = alternatives
        self.criteria = criteria
        self.alternatives_performances = self.directed_alternatives_performances(alternatives_performances, directions)
        self.weights = weights
        self.decimal_place = decimal_place
        self.generalized_criteria = generalized_criteria
        self.p_list = p_list
        self.q_list = q_list

    def directed_alternatives_performances(self,
                                           alternatives_performances: List[List[NumericValue]],
                                           directions: List[NumericValue]) -> List[List[NumericValue]]:
        for i in range(len(directions)):
            if directions[i] == 0:
                for j in range(len(alternatives_performances)):
                    alternatives_performances[j][i] = -alternatives_performances[j][i]

        return alternatives_performances

    def __deviations(self) -> List[List[List[NumericValue]]]:
        """
        Compares alternatives on criteria.

        :return: 3D matrix of deviations in evaluations on criteria
        """
        deviations = []
        for k in range(len(self.criteria)):
            comparisons = []
            for i in range(len(self.alternatives_performances)):
                comparison_direct = []
                for j in range(len(self.alternatives_performances)):
                    comparison_direct.append(
                        self.alternatives_performances[i][k] - self.alternatives_performances[j][k])
                comparisons.append(comparison_direct)
            deviations.append(comparisons)
        return deviations

    def __partialPreference(self) -> List[List[List[NumericValue]]]:
        """
        Calculates partial preference of every alternative over others at every criterion
        based on deviations using a method chosen by user.
        :return: partial preference indices
        """
        deviations = self.__deviations()
        ppIndices = []
        for k in range(len(self.criteria)):
            method = self.generalized_criteria[k]
            q = self.q_list[k]
            p = self.p_list[k]
            criterionIndices = []
            for i in range(len(self.alternatives_performances)):
                alternativeIndices = []
                for j in range(len(self.alternatives_performances)):
                    if method is PreferenceFunction.USUAL:
                        alternativeIndices.append(gc.usualCriterion(deviations[k][i][j]))
                    elif method is PreferenceFunction.U_SHAPE:
                        alternativeIndices.append(gc.uShapeCriterion(deviations[k][i][j], q))
                    elif method is PreferenceFunction.V_SHAPE:
                        alternativeIndices.append(gc.vShapeCriterion(deviations[k][i][j], p))
                    elif method is PreferenceFunction.LEVEL:
                        if q > p:
                            raise ValueError(
                                "incorrect threshold : q "
                                + str(q)
                                + " greater than p "
                                + str(p)
                            )
                        alternativeIndices.append(gc.levelCriterion(deviations[k][i][j], p, q))
                    elif method is PreferenceFunction.V_SHAPE_INDIFFERENCE:
                        if q > p:
                            raise ValueError(
                                "incorrect threshold : q "
                                + str(q)
                                + " greater than p "
                                + str(p)
                            )
                        alternativeIndices.append(gc.vShapeIndifferenceCriterion(deviations[k][i][j], p, q))
                    else:
                        raise ValueError(
                            "pref_func "
                            + str(method)
                            + " is not known."
                        )
                criterionIndices.append(alternativeIndices)
            ppIndices.append(criterionIndices)
        return ppIndices

    def computePreferenceIndices(self):
        """
        Calculates preference of every alternative over others based on partial preferences

        :return: preferences
        :return: partial preferences
        """
        partialPref = self.__partialPreference()
        preferences = []
        for i in range(len(self.alternatives_performances)):
            aggregatedPI = []
            for j in range(len(self.alternatives_performances)):
                Pi_A_B = 0
                for k in range(len(self.criteria)):
                    Pi_A_B += partialPref[k][i][j] * self.weights[k]
                aggregatedPI.append(Pi_A_B)
            preferences.append(aggregatedPI)

        return preferences, partialPref
