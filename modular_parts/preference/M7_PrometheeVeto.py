"""
This module calculates preference indices with veto thresholds

Implementation and naming of conventions are taken from
:cite:p:'Veto'.
"""
from core.aliases import NumericValue
import core.preference_commons as pc
import pandas as pd
from typing import Tuple, List, Union

__all__ = ["compute_veto"]

from core.input_validation import veto_validation


def compute_veto(
        alternatives_performances: pd.DataFrame,
        weights: pd.Series,
        veto_thresholds: pd.Series,
        directions: pd.Series,
        strong_veto: bool = True,
        profiles_performance: pd.DataFrame = None,
        decimal_place: NumericValue = 3,
        preferences=None) -> Union[
    Tuple[
        Union[pd.DataFrame, List[pd.DataFrame]],
        Union[pd.DataFrame, List[pd.DataFrame]]],
    Tuple[
        Union[pd.DataFrame, List[pd.DataFrame]],
        Union[pd.DataFrame, List[pd.DataFrame]],
        Union[pd.DataFrame, Tuple[pd.DataFrame]]]]:
    """
    Calculates veto of every alternative over other alternatives
    or profiles_performances based on partial veto

    :param alternatives_performances: Dataframe of alternatives' value at
        every criterion, index: alternatives, columns: criteria
    :param weights: Series with weights as values and criteria as index
    :param veto_thresholds: Series of veto threshold for each criterion,
        index: criteria
    :param directions: Series with directions of preference as values and
        criteria as index
    :param strong_veto: boolean value representing strong veto or discordance
        like veto
    :param profiles_performance: Dataframe of profiles' performance (value)
        at every criterion, index: profiles, columns: criteria
    :param decimal_place: the decimal place of the output numbers
    :param preferences: DataFrame of preference indices as value,
        alternatives/profiles as index and columns,
        if not None function returns already calculated overall
        preference instead of just veto
     
    :return: Tuple of DataFrame of overall veto (alternatives/profiles
        as index and columns) and DataFrame of partial veto indices
        (alternatives/profiles and criteria as index, alternatives/profiles as
        columns). With profiles, it's going to be Tuple of tuples of
        DataFrames of overall veto and DataFrames of partial
        veto indices. Additionally, if preferences given: DataFrame of
        overall preference (alternatives/profiles as index and columns) or
        tuple of DataFrames of overall preference with profiles.
    """
    # input data validation
    veto_validation(alternatives_performances, weights, veto_thresholds,
                    directions, strong_veto, profiles_performance,
                    decimal_place, preferences)

    alternatives = alternatives_performances.index
    criteria = weights.keys()

    # weights normalization
    weights = weights/sum(weights)

    # changing values of alternatives' performances according to direction
    # of criterion for further calculations
    alternatives_performances = pc.directed_alternatives_performances(
        alternatives_performances, directions)

    # check if partial preferences were calculated with profiles
    if profiles_performance is not None:
        categories_profiles = profiles_performance.index
        # changing values of profiles' performances according to direction
        # of criterion for further calculations
        profile_performance_table = pc.directed_alternatives_performances(
            profiles_performance, directions)
    else:
        categories_profiles = None
        profile_performance_table = None

    # calculating partial veto indices
    partial_vet = _partial_veto(veto_thresholds, criteria,
                                alternatives_performances,
                                profile_performance_table,
                                categories_profiles)

    # were the preferences calculated for profiles
    profiles = False

    # checking if categories_profiles exist
    if categories_profiles is None:
        # calculating veto indices for alternatives over alternatives
        veto = _vetoes(criteria, weights, strong_veto, partial_vet,
                       decimal_place, alternatives)
        partial_veto = partial_vet
    else:
        profiles = True
        # calculating veto indices for alternatives over profiles
        # and profiles over alternatives
        partial_veto = partial_vet[1], partial_vet[0]
        veto = (
            _vetoes(criteria, weights, strong_veto, partial_vet[1],
                    decimal_place,
                    categories_profiles,
                    alternatives),
            _vetoes(criteria, weights, strong_veto, partial_vet[0],
                    decimal_place,
                    alternatives,
                    categories_profiles))

    # check whether to calculate overall preference
    if preferences is not None:
        return veto, partial_veto, pc.overall_preference(preferences,
                                                         veto,
                                                         profiles,
                                                         decimal_place)
    else:
        return veto, partial_veto


def _vetoes(criteria: pd.Index, weights: pd.Series, strong_veto: bool,
            partial_veto: Union[
                pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]],
            decimal_place: NumericValue,
            i_iter: pd.Index, j_iter: pd.Index = None) -> pd.DataFrame:
    """
    Calculates aggregated veto indices.
    
    :param criteria: pd.Index with criteria indices
    :param weights: Series with weights as values and criteria as index
    :param strong_veto: boolean value representing strong veto or discordance
        like veto
    :param partial_veto: DataFrame of partial veto indices as
        value, alternatives/profiles and criteria as index and
        alternatives/profiles as columns
    :param decimal_place: the decimal place of the output numbers
    :param i_iter: alternatives or categories profiles
    :param j_iter: alternatives or categories profiles or None

    :return: DataFrame of veto indices as value and
        alternatives/profiles as index and columns
    """
    if j_iter is None:
        j_iter = i_iter
    vetoes = []
    index = partial_veto.loc[criteria[0]].index
    columns = partial_veto.loc[criteria[0]].columns
    for j in j_iter:
        aggregated_v = []
        for i in i_iter:
            pi_a_b = 0
            # aggregate partial veto indices from each criterion
            for k in criteria:
                if strong_veto:
                    # for strong veto single partial veto is enough to reject
                    # alternative preference over other alternative
                    if partial_veto.loc[k, j][i] == 1:
                        pi_a_b = 1
                        break
                else:
                    pi_a_b += partial_veto.loc[k, j][i] * weights[k]

            aggregated_v.append(round(pi_a_b, decimal_place))
        vetoes.append(aggregated_v)

    return pd.DataFrame(data=vetoes, index=index, columns=columns)


def _partial_veto(veto_thresholds: pd.Series, criteria: pd.Index,
                  alternatives_performances: pd.DataFrame,
                  profile_performances: pd.DataFrame,
                  categories_profiles: pd.Index
                  ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]:
    """
    Calculates partial veto of every alternative over other alternatives
    or profiles at every criterion based on deviations.

    :param veto_thresholds: Series of veto threshold for each criterion,
        index: criteria
    :param criteria: pd.Index with criteria indices
    :param alternatives_performances: Dataframe of alternatives' value at
        every criterion, index: alternatives, columns: criteria
    :param profile_performances: Dataframe of profiles' performance (value)
        at every criterion, index: profiles, columns: criteria
    :param categories_profiles: pd.Index with profiles' indices

    :return: DataFrame of partial veto indices as value,
        alternatives/profiles and criteria as index and alternatives/profiles
        as columns
    """
    deviations = pc.deviations(
        criteria=criteria,
        alternatives_performances=alternatives_performances,
        profiles_performances=profile_performances)
    if categories_profiles is None:
        # calculating veto partial indices for alternatives over alternatives
        # at every criterion
        pvetos = _veto_deep(veto_thresholds=veto_thresholds,
                            criteria=criteria, deviations=deviations,
                            i_iter=alternatives_performances,
                            j_iter=alternatives_performances)
    else:
        # calculating veto indices for alternatives over profiles
        # and profiles over alternatives at every criterion
        pvetos = (
            _veto_deep(veto_thresholds=veto_thresholds, criteria=criteria,
                       deviations=deviations[0],
                       i_iter=alternatives_performances,
                       j_iter=profile_performances),
            _veto_deep(veto_thresholds=veto_thresholds, criteria=criteria,
                       deviations=deviations[1],
                       i_iter=profile_performances,
                       j_iter=alternatives_performances))
    return pvetos


def _veto_deep(veto_thresholds: pd.Series, criteria: pd.Index,
               deviations: List[List[List[NumericValue]]],
               i_iter: pd.DataFrame, j_iter: pd.DataFrame) -> pd.DataFrame:
    """
    This function computes the veto indices for a given set of alternatives
    and criteria.

    :param veto_thresholds: Series of veto threshold for each criterion,
        index: criteria
    :param criteria: pd.Index with criteria indices
    :param deviations: 3D list of calculated deviations alternatives/profiles
        over alternatives/profiles at every criterion
    :param i_iter: pd.DataFrame of alternatives or categories profiles
        performances
    :param j_iter: pd.DataFrame alternatives or categories profiles
        performances or None

    :return: DataFrame of partial veto indices as value,
        alternatives/profiles and criteria as index and alternatives/profiles
        as columns
    """
    pvetos = []
    for k in range(criteria.size):
        v = veto_thresholds[k]
        criterion_indices = []
        for j in range(i_iter.shape[0]):
            alternative_vetoes = []
            for i in range(j_iter.shape[0]):
                if v is None:
                    alternative_vetoes.append(0)
                elif deviations[k][i][j] >= v:
                    alternative_vetoes.append(1)
                else:
                    alternative_vetoes.append(0)
            criterion_indices.append(alternative_vetoes)
        pvetos.append(criterion_indices)

    names = ['criteria'] + i_iter.index.names
    pvetos = pd.concat(
        [pd.DataFrame(data=x, index=i_iter.index, columns=j_iter.index) for x
         in pvetos],
        keys=criteria,
        names=names)
    return pvetos
