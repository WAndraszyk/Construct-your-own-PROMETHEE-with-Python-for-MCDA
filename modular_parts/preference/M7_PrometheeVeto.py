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
    Tuple[Union[pd.DataFrame, List[pd.DataFrame]], Union[
        pd.DataFrame, List[pd.DataFrame]]], pd.DataFrame, Tuple[
        pd.DataFrame]]:
    """
    Calculates veto of every alternative over other alternatives
    or profiles based on partial veto

    :param alternatives_performances: Dataframe of alternatives' value at
    every criterion
    :param weights: criteria with weights
    :param veto_thresholds: veto threshold for each criterion
    :param directions: directions of preference of criteria
    :param strong_veto: choose methode of calculating vetoes
    :param profiles_performance: Dataframe of profiles performance (value) at
    every criterion
    :param decimal_place: with this you can choose the decimal_place of the
     output numbers
    :param preferences: if not None function returns already calculated
     preference instead of just veto
    :return: veto
    :return: partial veto
    """
    veto_validation(alternatives_performances, weights, veto_thresholds,
                    directions, strong_veto, profiles_performance,
                    decimal_place, preferences)

    alternatives = alternatives_performances.index
    criteria = weights.keys()
    alternatives_performances = pc.directed_alternatives_performances(
        alternatives_performances, directions)
    if profiles_performance is not None:
        categories_profiles = profiles_performance.index
        profile_performance_table = pc.directed_alternatives_performances(
            profiles_performance, directions)
    else:
        categories_profiles = None
        profile_performance_table = None

    partialVet = _partial_veto(veto_thresholds, criteria,
                               alternatives_performances,
                               profile_performance_table,
                               categories_profiles)

    profiles = False
    if categories_profiles is None:
        veto = _vetoes(criteria, weights, strong_veto, partialVet,
                       decimal_place, alternatives)
        partial_veto = partialVet
    else:
        profiles = True
        partial_veto = partialVet[1], partialVet[0]
        veto = (
            _vetoes(criteria, weights, strong_veto, partialVet[1],
                    decimal_place,
                    categories_profiles,
                    alternatives),
            _vetoes(criteria, weights, strong_veto, partialVet[0],
                    decimal_place,
                    alternatives,
                    categories_profiles))
    if preferences is not None:
        return pc.overall_preference(preferences, veto, profiles,
                                     decimal_place)
    else:
        return veto, partial_veto


def _vetoes(criteria: pd.Index, weights: pd.Series, full_veto: bool,
            partial_veto: Union[
                pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]],
            decimal_place: NumericValue,
            i_iter: pd.Index, j_iter: pd.Index = None) -> pd.DataFrame:
    if j_iter is None:
        j_iter = i_iter
    Vetoes = []
    index = partial_veto.loc[criteria[0]].index
    columns = partial_veto.loc[criteria[0]].columns
    for j in j_iter:
        aggregated_v = []
        for i in i_iter:
            Pi_A_B = 0
            for k in criteria:
                if full_veto:
                    if partial_veto.loc[k, j][i] == 1:
                        Pi_A_B = 1
                        break
                else:
                    Pi_A_B += partial_veto.loc[k, j][i] * weights[k]

            aggregated_v.append(round(Pi_A_B, decimal_place))
        Vetoes.append(aggregated_v)

    return pd.DataFrame(data=Vetoes, index=index, columns=columns)


def _partial_veto(veto_thresholds: pd.Series, criteria: pd.Index,
                  alternatives_performances: pd.DataFrame,
                  profile_performance_table: pd.DataFrame,
                  categories_profiles: pd.Index
                  ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]:
    """
    Calculates partial veto of every alternative over other alternatives
    or profiles at every criterion based on deviations.

    :return: partial veto
    """
    deviations = pc.deviations(
        criteria=criteria,
        alternatives_performances=alternatives_performances,
        profile_performance_table=profile_performance_table)
    if categories_profiles is None:

        pvetos = _veto_deep(veto_thresholds=veto_thresholds,
                            criteria=criteria, deviations=deviations,
                            i_iter=alternatives_performances,
                            j_iter=alternatives_performances)
    else:
        pvetos = (
            _veto_deep(veto_thresholds=veto_thresholds, criteria=criteria,
                       deviations=deviations[0],
                       i_iter=alternatives_performances,
                       j_iter=profile_performance_table),
            _veto_deep(veto_thresholds=veto_thresholds, criteria=criteria,
                       deviations=deviations[1],
                       i_iter=profile_performance_table,
                       j_iter=alternatives_performances))
    return pvetos


def _veto_deep(veto_thresholds: pd.Series, criteria: pd.Index,
               deviations: List[Union[
                   List[List[NumericValue]], List[List[List[NumericValue]]]]],
               i_iter: pd.DataFrame, j_iter: pd.DataFrame) -> pd.DataFrame:
    pvetos = []
    for k in range(criteria.size):
        v = veto_thresholds[k]
        criterionIndices = []
        for j in range(i_iter.shape[0]):
            alternative_Vetoes = []
            for i in range(j_iter.shape[0]):
                if v is None:
                    alternative_Vetoes.append(0)
                elif deviations[k][i][j] >= v:
                    alternative_Vetoes.append(1)
                else:
                    alternative_Vetoes.append(0)
            criterionIndices.append(alternative_Vetoes)
        pvetos.append(criterionIndices)

    names = ['criteria'] + i_iter.index.names
    pvetos = pd.concat(
        [pd.DataFrame(data=x, index=i_iter.index, columns=j_iter.index) for x
         in pvetos],
        keys=criteria,
        names=names)
    return pvetos
