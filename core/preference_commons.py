from enum import Enum
import copy
from typing import List
import core.generalized_criteria as gc

import numpy as np

from core.aliases import NumericValue


class PreferenceFunction(Enum):
    """Enumeration of the preference functions."""

    USUAL = 1
    U_SHAPE = 2
    V_SHAPE = 3
    LEVEL = 4
    V_SHAPE_INDIFFERENCE = 5
    GAUSSIAN = 6


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


def deviations(criteria, alternatives_performances, profile_performance_table=None):
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


def pp_deep(criteria, p_list, q_list, s_list, generalized_criteria, deviations, i_iter, j_iter, decimal_place):
    ppIndices = []
    for k in range(len(criteria)):
        method = generalized_criteria[k]
        q = q_list[k]
        p = p_list[k]
        s = s_list[k]
        criterionIndices = []
        for i in range(len(i_iter)):
            alternativeIndices = []
            for j in range(len(j_iter)):
                if method is PreferenceFunction.USUAL:
                    alternativeIndices.append(gc.usualCriterion(deviations[k][i][j]))
                elif method is PreferenceFunction.U_SHAPE:
                    alternativeIndices.append(gc.uShapeCriterion(deviations[k][i][j], q))
                elif method is PreferenceFunction.V_SHAPE:
                    alternativeIndices.append(gc.vShapeCriterion(deviations[k][i][j], p, decimal_place))
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
                    alternativeIndices.append(gc.vShapeIndifferenceCriterion(deviations[k][i][j],
                                                                             p, q, decimal_place))
                elif method is PreferenceFunction.GAUSSIAN:
                    alternativeIndices.append(gc.gaussianCriterion(deviations[k][i][j], s))
                else:
                    raise ValueError(
                        "pref_func "
                        + str(method)
                        + " is not known."
                    )
            criterionIndices.append(alternativeIndices)
        ppIndices.append(criterionIndices)
    return ppIndices




def partialPreference(criteria, p_list, q_list, s_list, generalized_criteria,  decimal_place,
                      categories_profiles, alternatives_performances, profile_performance_table):
    """
    Calculates partial preference of every alternative over other alternatives
    or profiles at every criterion based on deviations using a method chosen by user.
    :return: partial preference indices
    """

    deviation = deviations(criteria=criteria, alternatives_performances=alternatives_performances, profile_performance_table = profile_performance_table)
    if categories_profiles is None:
        ppIndices = pp_deep(deviations=deviation, criteria=criteria, p_list=p_list,
                            q_list=q_list, s_list=s_list,
                            i_iter=alternatives_performances, j_iter=alternatives_performances,
                            generalized_criteria=generalized_criteria, decimal_place=decimal_place)
    else:
        ppIndices = [pp_deep(deviations=deviation[0], criteria=criteria, p_list=p_list,
                             q_list=q_list, s_list=s_list,
                             i_iter=alternatives_performances, j_iter=profile_performance_table,
                             generalized_criteria=generalized_criteria, decimal_place=decimal_place),
                     pp_deep(deviations=deviation[1], criteria=criteria, p_list=p_list,
                             q_list=q_list, s_list=s_list,
                             i_iter=profile_performance_table, j_iter=alternatives_performances,
                             generalized_criteria=generalized_criteria, decimal_place=decimal_place)
                     ]
    return ppIndices
