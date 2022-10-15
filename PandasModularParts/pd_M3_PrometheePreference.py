from enum import Enum
from core.aliases import NumericValue, PerformanceTable
from typing import List
import core.preference_commons as pc
import pandas as pd


class PreferenceFunction(Enum):
    """Enumeration of the preference functions."""

    USUAL = 1
    U_SHAPE = 2
    V_SHAPE = 3
    LEVEL = 4
    V_SHAPE_INDIFFERENCE = 5
    GAUSSIAN = 6


class PrometheePreference:
    def __init__(self, alternatives_performances: PerformanceTable, preference_thresholds: pd.Series,
                 indifference_thresholds: pd.Series, standard_deviations: pd.Series, generalized_criteria: pd.Series,
                 directions: pd.Series, weights: pd.Series,
                 profiles_performance: PerformanceTable = None,
                 decimal_place: NumericValue = 3):
        """
        :param alternatives_performances: Dataframe of alternatives' value at every criterion
        :param preference_thresholds: preference threshold for each criterion
        :param indifference_thresholds: indifference threshold for each criterion
        :param standard_deviations: standard deviation for each criterion
        :param generalized_criteria: list of preference functions
        :param directions: directions of preference of criteria
        :param weights: criteria with weights
        :param profiles_performance: Dataframe of profiles performance (value) at every criterion
        :param decimal_place: with this you can choose the decimal_place of the output numbers
        """

        self.alternatives = alternatives_performances.index
        self.criteria = weights.keys()
        self.alternatives_performances = pc.directed_alternatives_performances(alternatives_performances, directions)
        self.weights = weights
        self.decimal_place = decimal_place
        self.generalized_criteria = generalized_criteria
        self.preference_thresholds = preference_thresholds
        self.indifference_thresholds = indifference_thresholds
        self.standard_deviations = standard_deviations
        if profiles_performance is not None:
            self.categories_profiles = profiles_performance.keys()
            self.profile_performance_table = pc.directed_alternatives_performances(profiles_performance, directions)
        else:
            self.categories_profiles = None
            self.profile_performance_table = None

    def computePreferenceIndices(self):
        """
        Calculates preference of every alternative over other alternatives
        or profiles based on partial preferences

        :return: preferences
        :return: partial preferences
        """
        partialPref = pc.partial_preference(criteria=self.criteria, p_list=self.preference_thresholds,
                                            q_list=self.indifference_thresholds, s_list=self.standard_deviations,
                                            generalized_criteria=self.generalized_criteria,
                                            categories_profiles=self.categories_profiles,
                                            alternatives_performances=self.alternatives_performances,
                                            profile_performance_table=self.profile_performance_table)
        if self.categories_profiles is None:
            return self.__preferences(partialPref, self.alternatives), partialPref
        else:
            return (self.__preferences(partialPref[0], self.alternatives, self.categories_profiles),
                    self.__preferences(partialPref[1], self.categories_profiles, self.alternatives)
                    ), partialPref

    def __preferences(self, partialPref, alternatives, categories_profiles=None):
        weight_sum = sum(self.weights.values)
        if categories_profiles is None:
            categories_profiles = alternatives
        preferences = []
        for i in alternatives:
            aggregatedPI = []
            for j in categories_profiles:
                Pi_A_B = 0
                for k in self.criteria:
                    Pi_A_B += partialPref.loc[k,i][j] * self.weights[k]
                Pi_A_B = Pi_A_B / weight_sum
                aggregatedPI.append(round(Pi_A_B, self.decimal_place))
            preferences.append(aggregatedPI)

        preferences = pd.DataFrame(data=preferences, columns=categories_profiles, index=alternatives)
        return preferences
