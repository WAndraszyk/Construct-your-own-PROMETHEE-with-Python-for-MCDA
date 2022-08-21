import copy
from typing import List

import numpy as np

from core.aliases import NumericValue


def directed_alternatives_performances(alternatives_performances: List[List[NumericValue]],
                                       directions: List[NumericValue]) -> List[List[NumericValue]]:
    """
    Changes value of alternative performance to the opposite value if the direction of preference is
    min (represented by 0)

    :param alternatives_performances: 2D list of alternatives' value at every criterion
    :param directions: directions of preference of criteria
    :return: 2D list of alternatives' value at every criterion
    """
    copy_alternatives_performances = copy.deepcopy(alternatives_performances)
    for i in range(len(directions)):
        if directions[i] == 0:
            for j in range(len(alternatives_performances)):
                copy_alternatives_performances[j][i] = -alternatives_performances[j][i]

    return copy_alternatives_performances


def deviations(criteria, alternatives_performances, profile_performance_table=None) -> List[List[List[NumericValue]]]:
    """
    Compares alternatives on criteria.

    :return: 3D matrix of deviations in evaluations on criteria
    """

    def dev_calc(i_iter, j_iter, k):
        for i in range(len(i_iter)):
            comparison_direct = []
            for j in range(len(j_iter)):
                comparison_direct.append(i_iter[i][k] - j_iter[j][k])
            comparisons.append(comparison_direct)
        return comparisons

    deviations_list = []
    if profile_performance_table is None:
        for k in range(len(criteria)):
            comparisons = []
            deviations_list.append(dev_calc(alternatives_performances, alternatives_performances, k))
    else:
        deviations_part = []
        for k in range(len(criteria)):
            comparisons = []
            deviations_part.append(dev_calc(alternatives_performances, profile_performance_table, k))
        deviations_list.append(deviations_part)
        deviations_part = []
        for k in range(len(criteria)):
            comparisons = []
            deviations_part.append(dev_calc(profile_performance_table, alternatives_performances, k))
        deviations_list.append(deviations_part)

    return deviations_list


def overall_preference(preferences, discordances, profiles):
    """
    Combines preference and discordance/veto indices to compute overall preference

    :param preferences: aggregated preference indices
    :param discordances: aggregated discordance/veto indices
    :param profiles: were the preferences and discordance/veto calculated with profiles
    :returns: overall preference indices
    """
    if profiles:
        for n in range(len(discordances)):
            for i in range(len(discordances[n])):
                for j in range(len(discordances[n][i])):
                    discordances[n][i][j] = 1 - discordances[n][i][j]
        overall_preferences = (np.multiply(preferences[0], discordances[0]).tolist(),
                               np.multiply(preferences[1], discordances[1]).tolist())
    else:
        for n in range(len(discordances)):
            for i in range(len(discordances[n])):
                discordances[n][i] = 1 - discordances[n][i]
        overall_preferences = np.multiply(preferences, discordances).tolist()

    return overall_preferences
