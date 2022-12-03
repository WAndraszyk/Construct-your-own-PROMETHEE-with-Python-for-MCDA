import copy
from typing import List, Tuple, Union

from core.aliases import PerformanceTable, PreferencePartialTable, DeviationsTable, NumericValue
from core.enums import GeneralCriterion, Direction
import core.generalized_criteria as gc

import pandas as pd


def directed_alternatives_performances(alternatives_performances: pd.DataFrame,
                                       directions: pd.Series) -> pd.DataFrame:
    """
    Changes value of alternative performance to the opposite value if the direction of preference is
    min (represented by 0)

    :param alternatives_performances: 2D list of alternatives' value at every criterion
    :param directions: directions of preference of criteria
    :return: 2D list of alternatives' value at every criterion
    """
    copy_alternatives_performances = copy.deepcopy(alternatives_performances)
    for direction in directions.keys():
        if directions[direction] == 0 or directions[direction] == Direction.MIN:
            copy_alternatives_performances[direction] = copy_alternatives_performances[direction] * -1

    return copy_alternatives_performances


def deviations(criteria: pd.Index, alternatives_performances: pd.DataFrame,
               profile_performance_table: pd.DataFrame = None
               ) -> DeviationsTable:
    """
    Compares alternatives on criteria.

    :return: 3D matrix of deviations in evaluations on criteria
    """

    def dev_calc(i_iter: pd.DataFrame, j_iter: pd.DataFrame, n):
        for _, i in i_iter.iterrows():
            comparison_direct = []
            for _, j in j_iter.iterrows():
                comparison_direct.append(i[n] - j[n])
            comparisons.append(comparison_direct)
        return comparisons

    deviations_list = []
    if profile_performance_table is None:
        for k in criteria:
            comparisons = []
            deviations_list.append(dev_calc(alternatives_performances, alternatives_performances, k))
    else:
        deviations_part = []
        for k in criteria:
            comparisons = []
            deviations_part.append(dev_calc(alternatives_performances, profile_performance_table, k))
        deviations_list.append(deviations_part)
        deviations_part = []
        for k in criteria:
            comparisons = []
            deviations_part.append(dev_calc(profile_performance_table, alternatives_performances, k))
        deviations_list.append(deviations_part)

    return deviations_list


def pp_deep(criteria: pd.Index, p_list: pd.Series, q_list: pd.Series, s_list: pd.Series,
            generalized_criteria: pd.Series, deviations: DeviationsTable, i_iter: PerformanceTable,
            j_iter: PerformanceTable) -> pd.DataFrame:
    ppIndices = []
    for k in range(len(criteria)):
        method = generalized_criteria[k]
        q = q_list[k]
        p = p_list[k]
        s = s_list[k]
        criterionIndices = []
        for i in range(i_iter.shape[0]):
            alternativeIndices = []
            for j in range(j_iter.shape[0]):
                if method is GeneralCriterion.USUAL:
                    alternativeIndices.append(gc.usual_criterion(deviations[k][i][j]))
                elif method is GeneralCriterion.U_SHAPE:
                    alternativeIndices.append(gc.u_shape_criterion(deviations[k][i][j], q))
                elif method is GeneralCriterion.V_SHAPE:
                    alternativeIndices.append(gc.v_shape_criterion(deviations[k][i][j], p))
                elif method is GeneralCriterion.LEVEL:
                    if q > p:
                        raise ValueError(
                            "incorrect threshold : q "
                            + str(q)
                            + " greater than p "
                            + str(p)
                        )
                    alternativeIndices.append(gc.level_criterion(deviations[k][i][j], p, q))
                elif method is GeneralCriterion.V_SHAPE_INDIFFERENCE:
                    if q > p:
                        raise ValueError(
                            "incorrect threshold : q "
                            + str(q)
                            + " greater than p "
                            + str(p)
                        )
                    alternativeIndices.append(gc.v_shape_indifference_criterion(deviations[k][i][j],
                                                                                p, q))
                elif method is GeneralCriterion.GAUSSIAN:
                    alternativeIndices.append(gc.gaussian_criterion(deviations[k][i][j], s))
                else:
                    raise ValueError(
                        "pref_func "
                        + str(method)
                        + " is not known."
                    )
            criterionIndices.append(alternativeIndices)
        ppIndices.append(criterionIndices)
    names = ['criteria'] + i_iter.index.names
    ppIndices = pd.concat([pd.DataFrame(data=x, index=i_iter.index, columns=j_iter.index) for x in ppIndices],
                          keys=criteria,
                          names=names)

    return ppIndices


def partial_preference(criteria: pd.Index, p_list: pd.Series, q_list: pd.Series, s_list: pd.Series,
                       generalized_criteria: pd.Series, categories_profiles: pd.Index,
                       alternatives_performances: PerformanceTable,
                       profile_performance_table: PerformanceTable) -> PreferencePartialTable:
    """
    Calculates partial preference of every alternative over other alternatives
    or profiles at every criterion based on deviations using a method chosen by user.
    :return: partial preference indices
    """

    deviation = deviations(criteria=criteria, alternatives_performances=alternatives_performances,
                           profile_performance_table=profile_performance_table)
    if categories_profiles is None:
        ppIndices = pp_deep(deviations=deviation, criteria=criteria, p_list=p_list,
                            q_list=q_list, s_list=s_list,
                            i_iter=alternatives_performances, j_iter=alternatives_performances,
                            generalized_criteria=generalized_criteria)
    else:
        ppIndices = (pp_deep(deviations=deviation[0], criteria=criteria, p_list=p_list,
                             q_list=q_list, s_list=s_list,
                             i_iter=alternatives_performances, j_iter=profile_performance_table,
                             generalized_criteria=generalized_criteria),
                     pp_deep(deviations=deviation[1], criteria=criteria, p_list=p_list,
                             q_list=q_list, s_list=s_list,
                             i_iter=profile_performance_table, j_iter=alternatives_performances,
                             generalized_criteria=generalized_criteria))
    return ppIndices


def overall_preference(preferences: Union[pd.DataFrame, Tuple[pd.DataFrame]],
                       discordances: Union[pd.DataFrame, Tuple[pd.DataFrame]],
                       profiles: bool, decimal_place: NumericValue) -> Union[pd.DataFrame, Tuple[pd.DataFrame]]:
    """
    Combines preference and discordance/veto indices to compute overall preference

    :param preferences: aggregated preference indices
    :param discordances: aggregated discordance/veto indices
    :param profiles: were the preferences and discordance/veto calculated with profiles
    :param decimal_place: with this you can choose the decimal_place of the output numbers
    :returns: overall preference indices
    """
    if profiles:
        for discordance in discordances:
            for n in discordance.index:
                for i in discordance.columns:
                    discordance[n][i] = 1 - discordance[n][i]
        overall_preferences = (preferences[0] * discordances[0], preferences[1] * discordances[1])
    else:
        for n in discordances.index:
            for i in discordances.columns:
                discordances[n][i] = 1 - discordances[n][i]
        overall_preferences = preferences * discordances
    if type(overall_preferences) == tuple:
        for i in range(2):
            overall_preferences = overall_preferences[0].round(decimal_place), overall_preferences[1].round(
                decimal_place)
    else:
        overall_preferences = overall_preferences.round(decimal_place)
    return overall_preferences


def criteria_series(criteria: pd.Index, weights: List[float]) -> pd.Series:
    """
    Connect criterion name with its weight.

    :param criteria: criteria names as list of string.
    :param weights: criteria weights as list of Numeric Values.

    :return: dictionary of connection.
    """
    return pd.Series(weights, criteria)
