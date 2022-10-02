from enum import Enum
from core.aliases import NumericValue
from typing import List
import core.preference_commons as pc


class PreferenceFunction(Enum):
    """Enumeration of the preference functions."""

    USUAL = 1
    U_SHAPE = 2
    V_SHAPE = 3
    LEVEL = 4
    V_SHAPE_INDIFFERENCE = 5
    GAUSSIAN = 6


class PrometheePreference:
    def __init__(self,
                 alternatives,
                 criteria,
                 alternatives_performances: List[List[NumericValue]],
                 weights: List[NumericValue],
                 p_list: List[NumericValue],
                 q_list: List[NumericValue],
                 s_list: List[NumericValue],
                 generalized_criteria,
                 directions: List[NumericValue],
                 categories_profiles: List[str] = None,
                 profile_performance_table: List[List[NumericValue]] = None,
                 decimal_place: NumericValue = 3):
        """
        :param alternatives: list of alternatives names
        :param criteria: list of criteria
        :param alternatives_performances: 2D list of alternatives' value at every criterion
        :param weights: list of weights
        :param p_list: list of preference threshold for each criterion
        :param q_list: list of indifference threshold for each criterion
        :param s_list: list of standard deviation for each criterion
        :param generalized_criteria: list of preference functions
        :param directions: directions of preference of criteria
        :param decimal_place: with this you can choose the decimal_place of the output numbers
        :param categories_profiles: list of profiles (names, strings)
        :param profile_performance_table: 2D list of profiles performance (value) at every criterion
        """

        self.alternatives = alternatives
        self.criteria = criteria
        self.alternatives_performances = pc.directed_alternatives_performances(alternatives_performances, directions)
        self.weights = weights
        self.decimal_place = decimal_place
        self.generalized_criteria = generalized_criteria
        self.p_list = p_list
        self.q_list = q_list
        self.s_list = s_list
        self.categories_profiles = categories_profiles
        if profile_performance_table is not None:
            self.profile_performance_table = pc.directed_alternatives_performances(profile_performance_table,
                                                                                   directions)
        else:
            self.profile_performance_table = profile_performance_table

    def computePreferenceIndices(self):
        """
        Calculates preference of every alternative over other alternatives
        or profiles based on partial preferences

        :return: preferences
        :return: partial preferences
        """
        partialPref = pc.partial_preference(criteria=self.criteria, p_list=self.p_list,
                                            q_list=self.q_list, s_list=self.s_list,
                                            generalized_criteria=self.generalized_criteria,
                                            categories_profiles=self.categories_profiles,
                                            alternatives_performances=self.alternatives_performances,
                                            profile_performance_table=self.profile_performance_table)
        if self.categories_profiles is None:
            return self.__preferences(partialPref, self.alternatives_performances), partialPref
        else:
            return (self.__preferences(partialPref[0], self.alternatives_performances, self.profile_performance_table),
                    self.__preferences(partialPref[1], self.profile_performance_table, self.alternatives_performances)
                    ), partialPref

    def __preferences(self, partialPref, i_iter, j_iter=None):
        weight_sum = 0
        for i in self.weights:
            weight_sum += i
        if j_iter is None:
            j_iter = i_iter
        preferences = []
        for i in range(len(i_iter)):
            aggregatedPI = []
            for j in range(len(j_iter)):
                Pi_A_B = 0
                for k in range(len(self.criteria)):
                    Pi_A_B += partialPref[k][i][j] * self.weights[k]
                Pi_A_B = Pi_A_B/weight_sum
                aggregatedPI.append(round(Pi_A_B, self.decimal_place))
            preferences.append(aggregatedPI)

        return preferences
