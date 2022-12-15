import copy
import pandas as pd
import core.generalized_criteria as gc
from typing import List, Tuple, Union
from core.aliases import NumericValue
from core.enums import GeneralCriterion, Direction


def directed_alternatives_performances(
        alternatives_performances: pd.DataFrame,
        directions: pd.Series) -> pd.DataFrame:
    """
    Changes value of alternative performance to the opposite value if
    the direction of preference is min (represented by 0)

    :param alternatives_performances: Dataframe of alternatives' value at
        every criterion, index: alternatives, columns: criteria
    :param directions: Series with directions of preference as values and
        criteria as index
    :return: Dataframe of alternatives' redirected value at every criterion,
        index: alternatives, columns: criteria
    """
    copy_alternatives_performances = copy.deepcopy(alternatives_performances)
    for direction in directions.keys():
        if directions[direction] == 0 or \
                directions[direction] == Direction.MIN:
            copy_alternatives_performances[direction] = \
                copy_alternatives_performances[direction] * -1

    return copy_alternatives_performances


def deviations(criteria: pd.Index, alternatives_performances: pd.DataFrame,
               profiles_performances: pd.DataFrame = None
               ) -> List[Union[List[List[NumericValue]],
                               List[List[List[NumericValue]]]]]:
    """
    Compares alternatives on criteria.

    :param criteria: pd.Index with criteria indices
    :param alternatives_performances: Dataframe of alternatives' value at
        every criterion, index: alternatives, columns: criteria
    :param profiles_performances: Dataframe of profiles' value at
        every criterion, index: profiles, columns: criteria
    :return: 3D list of calculated deviations alternatives over
        alternatives at every criterion or 4D list of calculated deviations
        alternatives over profiles and profiles over alternatives at every
        criterion
    """

    def dev_calc(i_iter: pd.DataFrame, j_iter: pd.DataFrame, n: int
                 ) -> List[List[NumericValue]]:
        """
        Calculates deviation in performance between alternatives on
        given criterion.

        :param i_iter: pd.DataFrame with alternatives or categories profiles
        performances
        :param j_iter: pd.DataFrame alternatives or categories profiles
            performances or None
        :param n: criterion

        :return: 2D list with deviations
        """
        for _, i in i_iter.iterrows():
            comparison_direct = []
            for _, j in j_iter.iterrows():
                comparison_direct.append(i[n] - j[n])
            comparisons.append(comparison_direct)
        return comparisons

    deviations_list = []
    # checking if categories_profiles exist
    if profiles_performances is None:
        for k in criteria:
            comparisons = []
            # calculating deviation for alternatives over alternatives
            deviations_list.append(dev_calc(alternatives_performances,
                                            alternatives_performances, k))
    else:
        deviations_part = []
        # calculating deviation for alternatives over profiles
        for k in criteria:
            comparisons = []
            deviations_part.append(dev_calc(alternatives_performances,
                                            profiles_performances, k))
        deviations_list.append(deviations_part)
        deviations_part = []
        for k in criteria:
            comparisons = []
            # calculating deviation for profiles over alternatives
            deviations_part.append(dev_calc(profiles_performances,
                                            alternatives_performances, k))
        deviations_list.append(deviations_part)

    return deviations_list


def pp_deep(criteria: pd.Index, preference_thresholds: pd.Series,
            indifference_thresholds: pd.Series,
            s_parameters: pd.Series, generalized_criteria: pd.Series,
            deviations_table: List[List[List[NumericValue]]],
            i_iter: pd.DataFrame, j_iter: pd.DataFrame) -> pd.DataFrame:
    """
    This function computes the preference indices for a given set of
    alternatives and criteria.

    :param criteria: pd.Index with criteria indices
     :param preference_thresholds: Series of preference threshold for
        each criterion, index: criteria
    :param indifference_thresholds: Series of indifference threshold for
        each criterion, index: criteria
    :param s_parameters: Series of s parameter for each criterion, s parameter
        is a threshold used in Gaussian Criterion, it's defined as an
        intermediate value between indifference and preference threshold,
        index: criteria
    :param generalized_criteria: Series with preference functions as values
        and criteria as index
    :param deviations_table: 3D list of calculated deviations
        alternatives/profiles over alternatives/profiles at every criterion
    :param i_iter: pd.DataFrame of alternatives or categories profiles
        performances
    :param j_iter: pd.DataFrame alternatives or categories profiles
        performances or None

    :return: DataFrame of partial preference indices as value,
        alternatives/profiles and criteria as index and alternatives/profiles
        as columns
    """
    pp_indices = []
    for k in range(len(criteria)):
        method = generalized_criteria[k]
        q = indifference_thresholds[k]
        p = preference_thresholds[k]
        s = s_parameters[k]
        criterion_indices = []
        for i in range(i_iter.shape[0]):
            alternative_indices = []
            for j in range(j_iter.shape[0]):
                # calculating partial preference depending on generalised
                # criterion
                if method is GeneralCriterion.USUAL:
                    alternative_indices.append(gc.usual_criterion(
                        deviations_table[k][i][j]))
                elif method is GeneralCriterion.U_SHAPE:
                    alternative_indices.append(gc.u_shape_criterion(
                        deviations_table[k][i][j], q))
                elif method is GeneralCriterion.V_SHAPE:
                    alternative_indices.append(gc.v_shape_criterion(
                        deviations_table[k][i][j], p))
                elif method is GeneralCriterion.LEVEL:
                    if q > p:
                        raise ValueError(
                            "incorrect threshold : q "
                            + str(q)
                            + " greater than p "
                            + str(p)
                        )
                    alternative_indices.append(gc.level_criterion(
                        deviations_table[k][i][j], p, q))
                elif method is GeneralCriterion.V_SHAPE_INDIFFERENCE:
                    if q > p:
                        raise ValueError(
                            "incorrect threshold : q "
                            + str(q)
                            + " greater than p "
                            + str(p)
                        )
                    alternative_indices.append(
                        gc.v_shape_indifference_criterion(
                            deviations_table[k][i][j], p, q))
                elif method is GeneralCriterion.GAUSSIAN:
                    alternative_indices.append(gc.gaussian_criterion(
                        deviations_table[k][i][j], s))
                else:
                    raise ValueError(
                        "pref_func "
                        + str(method)
                        + " is not known."
                    )
            criterion_indices.append(alternative_indices)
        pp_indices.append(criterion_indices)
    names = ['criteria'] + i_iter.index.names
    pp_indices = pd.concat([pd.DataFrame(data=x, index=i_iter.index,
                                         columns=j_iter.index)
                            for x in pp_indices],
                           keys=criteria,
                           names=names)

    return pp_indices


def partial_preference(criteria: pd.Index, preference_thresholds: pd.Series,
                       indifference_thresholds: pd.Series,
                       s_parameters: pd.Series,
                       generalized_criteria: pd.Series,
                       categories_profiles: pd.Index,
                       alternatives_performances: pd.DataFrame,
                       profiles_performances: pd.DataFrame
                       ) -> Union[pd.DataFrame,
                                  Tuple[pd.DataFrame, pd.DataFrame]]:
    """
    Calculates partial preference of every alternative over other
    alternatives or profiles at every criterion based on deviations
    using a method chosen by user.

    :param criteria: pd.Index with criteria indices
    :param preference_thresholds: Series of preference threshold for
        each criterion, index: criteria
    :param indifference_thresholds: Series of indifference threshold for
        each criterion, index: criteria
    :param s_parameters: Series of s parameter for each criterion, s parameter
        is a threshold used in Gaussian Criterion, it's defined as an
        intermediate value between indifference and preference threshold,
        index: criteria
    :param generalized_criteria: Series with preference functions as values
        and criteria as index
    :param alternatives_performances: Dataframe of alternatives' value at
        every criterion
    :param profiles_performances: Dataframe of profiles' value at
        every criterion
    :param categories_profiles: pd.Index (list) of categories profiles

    :return: DataFrame of partial preferences (alternatives/profiles and
        criteria as index, alternatives/profiles as columns). With profiles,
        it's going to be Tuple partial preferences DataFrames.
    """

    # calculating deviation
    dvt = deviations(criteria=criteria,
                     alternatives_performances=alternatives_performances,
                     profiles_performances=profiles_performances
                     )
    # checking if categories_profiles exist
    if categories_profiles is None:
        # calculating partial indices for alternatives over
        # alternatives at every criterion
        pp_indices = pp_deep(deviations_table=dvt, criteria=criteria,
                             preference_thresholds=preference_thresholds,
                             indifference_thresholds=indifference_thresholds,
                             s_parameters=s_parameters,
                             i_iter=alternatives_performances,
                             j_iter=alternatives_performances,
                             generalized_criteria=generalized_criteria)
    else:
        # calculating preference indices for alternatives over profiles
        # and profiles over alternatives at every criterion
        pp_indices = (
            pp_deep(deviations_table=dvt[0], criteria=criteria,
                    preference_thresholds=preference_thresholds,
                    indifference_thresholds=indifference_thresholds,
                    s_parameters=s_parameters,
                    i_iter=alternatives_performances,
                    j_iter=profiles_performances,
                    generalized_criteria=generalized_criteria),
            pp_deep(deviations_table=dvt[1], criteria=criteria,
                    preference_thresholds=preference_thresholds,
                    indifference_thresholds=indifference_thresholds,
                    s_parameters=s_parameters,
                    i_iter=profiles_performances,
                    j_iter=alternatives_performances,
                    generalized_criteria=generalized_criteria))
    return pp_indices


def overall_preference(preferences: Union[pd.DataFrame, Tuple[pd.DataFrame]],
                       discordances: Union[pd.DataFrame, Tuple[pd.DataFrame]],
                       profiles: bool, decimal_place: NumericValue
                       ) -> Union[pd.DataFrame, Tuple[pd.DataFrame]]:
    """
    Combines preference and discordance/veto indices to compute overall
    preference

    :param preferences: aggregated preference indices
    :param discordances: aggregated discordance/veto indices
    :param profiles: were the preferences and discordance/veto calculated
        with profiles
    :param decimal_place: the decimal place of the output numbers
    :returns: overall preference indices
    """
    if profiles:
        for discordance in discordances:
            for n in discordance.index:
                for i in discordance.columns:
                    discordance[n][i] = 1 - discordance[n][i]
        overall_preferences = (preferences[0] * discordances[0],
                               preferences[1] * discordances[1])
    else:
        for n in discordances.index:
            for i in discordances.columns:
                discordances[n][i] = 1 - discordances[n][i]
        overall_preferences = preferences * discordances
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
