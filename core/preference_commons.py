import copy
import pandas as pd
import core.generalized_criteria as gc
from typing import List, Tuple, Union
from core.aliases import NumericValue
from core.enums import GeneralCriterion, Direction


def directed_alternatives_performances(alternatives_performances: pd.DataFrame
                                       , directions: pd.Series
                                       ) -> pd.DataFrame:
    """
    Changes value of alternative performance to the opposite value if
    the direction of preference is min (represented by 0)

    :param alternatives_performances: 2D list of alternatives' value at
        every criterion
    :param directions: directions of preference of criteria
    :return: 2D list of alternatives' value at every criterion
    """
    copy_alternatives_performances = copy.deepcopy(alternatives_performances)
    for direction in directions.keys():
        if directions[direction] == 0 or \
                directions[direction] == Direction.MIN:
            copy_alternatives_performances[direction] = \
                copy_alternatives_performances[direction] * -1

    return copy_alternatives_performances


def deviations(criteria: pd.Index, alternatives_performances: pd.DataFrame,
               profile_performance_table: pd.DataFrame = None
               ) -> List[Union[List[List[NumericValue]],
                               List[List[List[NumericValue]]]]]:
    """
    Compares alternatives on criteria.

    :param criteria: list of criteria
    :param alternatives_performances: 2D list of alternatives' value at
        every criterion
    :param profile_performance_table: Dataframe of profiles' value at
        every criterion
    :return: 3D matrix of deviations in evaluations on criteria
    """

    def dev_calc(i_iter: pd.DataFrame, j_iter: pd.DataFrame, n: int
                 ) -> List[List[NumericValue]]:
        """
        Calculates deviation in performance between alternatives on
        given criterion.

        :param i_iter: alternatives or categories profiles performances
        :param j_iter: alternatives or categories profiles performances
            or None
        :param n: criterion

        :return: deviation
        """
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
            deviations_list.append(dev_calc(alternatives_performances,
                                            alternatives_performances, k))
    else:
        deviations_part = []
        for k in criteria:
            comparisons = []
            deviations_part.append(dev_calc(alternatives_performances,
                                            profile_performance_table, k))
        deviations_list.append(deviations_part)
        deviations_part = []
        for k in criteria:
            comparisons = []
            deviations_part.append(dev_calc(profile_performance_table,
                                            alternatives_performances, k))
        deviations_list.append(deviations_part)

    return deviations_list


def pp_deep(criteria: pd.Index, preference_thresholds: pd.Series,
            indifference_thresholds: pd.Series,
            s_parameters: pd.Series, generalized_criteria: pd.Series,
            deviations: List[Union[List[List[NumericValue]],
                                   List[List[List[NumericValue]]]]],
            i_iter: pd.DataFrame, j_iter: pd.DataFrame) -> pd.DataFrame:
    """
    This function computes the preference indices for a given set of
    alternatives and criteria.

    :param criteria: list of criteria
    :param preference_thresholds: preference thresholds
    :param indifference_thresholds: indifference thresholds
    :param s_parameters: s parameters
    :param generalized_criteria: list of preference functions
    :param deviations: list of calculated deviations
    :param i_iter: alternatives or categories profiles performances
    :param j_iter: alternatives or categories profiles performances
        or None

    :return: partial preference indices
    """
    ppIndices = []
    for k in range(len(criteria)):
        method = generalized_criteria[k]
        q = indifference_thresholds[k]
        p = preference_thresholds[k]
        s = s_parameters[k]
        criterionIndices = []
        for i in range(i_iter.shape[0]):
            alternativeIndices = []
            for j in range(j_iter.shape[0]):
                if method is GeneralCriterion.USUAL:
                    alternativeIndices.append(gc.usual_criterion(
                        deviations[k][i][j]))
                elif method is GeneralCriterion.U_SHAPE:
                    alternativeIndices.append(gc.u_shape_criterion(
                        deviations[k][i][j], q))
                elif method is GeneralCriterion.V_SHAPE:
                    alternativeIndices.append(gc.v_shape_criterion(
                        deviations[k][i][j], p))
                elif method is GeneralCriterion.LEVEL:
                    if q > p:
                        raise ValueError(
                            "incorrect threshold : q "
                            + str(q)
                            + " greater than p "
                            + str(p)
                        )
                    alternativeIndices.append(gc.level_criterion(
                        deviations[k][i][j], p, q))
                elif method is GeneralCriterion.V_SHAPE_INDIFFERENCE:
                    if q > p:
                        raise ValueError(
                            "incorrect threshold : q "
                            + str(q)
                            + " greater than p "
                            + str(p)
                        )
                    alternativeIndices.append(
                        gc.v_shape_indifference_criterion(
                            deviations[k][i][j], p, q))
                elif method is GeneralCriterion.GAUSSIAN:
                    alternativeIndices.append(gc.gaussian_criterion(
                        deviations[k][i][j], s))
                else:
                    raise ValueError(
                        "pref_func "
                        + str(method)
                        + " is not known."
                    )
            criterionIndices.append(alternativeIndices)
        ppIndices.append(criterionIndices)
    names = ['criteria'] + i_iter.index.names
    ppIndices = pd.concat([pd.DataFrame(data=x, index=i_iter.index,
                                        columns=j_iter.index)
                           for x in ppIndices],
                          keys=criteria,
                          names=names)

    return ppIndices


def partial_preference(criteria: pd.Index, preference_thresholds: pd.Series,
                       indifference_thresholds: pd.Series,
                       s_parameters: pd.Series,
                       generalized_criteria: pd.Series,
                       categories_profiles: pd.Index,
                       alternatives_performances: pd.DataFrame,
                       profile_performance_table: pd.DataFrame
                       ) -> Union[pd.DataFrame,
                                  Tuple[pd.DataFrame, pd.DataFrame]]:
    """
    Calculates partial preference of every alternative over other
    alternatives or profiles at every criterion based on deviations
    using a method chosen by user.

    :param criteria: list of criteria
    :param preference_thresholds: preference thresholds
    :param indifference_thresholds: indifference thresholds
    :param s_parameters: s parameters
    :param generalized_criteria: list of preference functions
    :param alternatives_performances: Dataframe of alternatives' value at
        every criterion
    :param profile_performance_table: Dataframe of profiles' value at
        every criterion
    :param categories_profiles: list of categories profiles
    :return: partial preference indices
    """

    deviation = deviations(criteria=criteria,
                           alternatives_performances=alternatives_performances
                           ,
                           profile_performance_table=profile_performance_table
                           )
    if categories_profiles is None:
        ppIndices = pp_deep(deviations=deviation, criteria=criteria,
                            preference_thresholds=preference_thresholds,
                            indifference_thresholds=indifference_thresholds,
                            s_parameters=s_parameters,
                            i_iter=alternatives_performances,
                            j_iter=alternatives_performances,
                            generalized_criteria=generalized_criteria)
    else:
        ppIndices = (pp_deep(deviations=deviation[0], criteria=criteria,
                             preference_thresholds=preference_thresholds,
                             indifference_thresholds=indifference_thresholds,
                             s_parameters=s_parameters,
                             i_iter=alternatives_performances,
                             j_iter=profile_performance_table,
                             generalized_criteria=generalized_criteria),
                     pp_deep(deviations=deviation[1], criteria=criteria,
                             preference_thresholds=preference_thresholds,
                             indifference_thresholds=indifference_thresholds,
                             s_parameters=s_parameters,
                             i_iter=profile_performance_table,
                             j_iter=alternatives_performances,
                             generalized_criteria=generalized_criteria))
    return ppIndices


def overall_preference(preferences: Union[pd.DataFrame, Tuple[pd.DataFrame]],
                       discordances: Union[pd.DataFrame, Tuple[pd.DataFrame]],
                       profiles: bool, decimal_place: NumericValue
                       ) -> Union[pd.DataFrame, Tuple[pd.DataFrame]]:
    """
    Combines preference and discordance/veto indices to compute overall
    preference

    :param preferences: DataFrame with aggregated preference indices as
        values, alternatives/profiles as index and alternatives/profiles as
        columns
    :param discordances: DataFrame with aggregated discordance/veto indices as
        values, alternatives/profiles as index and alternatives/profiles as
        columns
    :param profiles: were the preferences and discordance/veto calculated
        with profiles
    :param decimal_place: the decimal place of the output numbers

    :returns: DataFrame of overall preference (alternatives/profiles as index
     and columns) or tuple of DataFrames of overall preference with profiles.
    """
    if profiles:
        # calculating overall preference for both preference matrices
        # if profiles
        for discordance in discordances:
            for n in discordance.index:
                for i in discordance.columns:
                    discordance[n][i] = 1 - discordance[n][i]
        overall_preferences = (preferences[0] * discordances[0],
                               preferences[1] * discordances[1])
    else:
        # calculating overall preference
        for n in discordances.index:
            for i in discordances.columns:
                discordances[n][i] = 1 - discordances[n][i]
        overall_preferences = preferences * discordances

    # round preferences to decimal place
    if type(overall_preferences) == tuple:
        for i in range(2):
            overall_preferences = \
                overall_preferences[0].round(decimal_place), \
                overall_preferences[1].round(decimal_place)
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
    return pd.Series(weights, criteria, name="weights")
