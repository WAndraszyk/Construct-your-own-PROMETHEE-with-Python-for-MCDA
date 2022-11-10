from typing import List, Union
from core.preference_commons import PreferenceFunction
from core.aliases import NumericValue, PerformanceTable
import core.generalized_criteria as gc
import core.preference_commons as pc
import pandas as pd
__all__ = ['compute_reinforced_preference']

def compute_reinforced_preference(alternatives_performances: PerformanceTable,
                                  preference_thresholds: pd.Series,
                                  indifference_thresholds: pd.Series,
                                  generalized_criteria: pd.Series,
                                  directions: pd.Series,
                                  reinforced_preference_thresholds: pd.Series,
                                  reinforcement_factors: pd.Series,
                                  weights: pd.Series,
                                  profiles_performance: PerformanceTable = None,
                                  decimal_place: NumericValue = 3) -> Union[pd.DataFrame, tuple[pd.DataFrame]]:
    """
    Calculates preference of every alternative over other alternatives
    or profiles based on partial preferences.
    Includes reinforced preference effect.

    :param alternatives_performances: Dataframe of alternatives' value at every criterion
    :param weights: criteria with weights
    :param generalized_criteria: method used for computing partial preference indices
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param generalized_criteria: list of preference functions
    :param directions: directions of preference of criteria
    :param reinforced_preference_thresholds: list of reinforced preference threshold for each criterion
    :param reinforcement_factors: list of reinforcement factor for each criterion
    :param weights: criteria with weights
    :param profiles_performance: Dataframe of profiles performance (value) at every criterion
    :param decimal_place: with this you can choose the decimal_place of the output numbers

    :return: preferences
    :return: partial preferences
    """
    criteria = weights.keys()
    alternatives_performances = pc.directed_alternatives_performances(alternatives_performances, directions)
    weights = weights
    generalized_criteria = generalized_criteria
    preference_thresholds = preference_thresholds
    indifference_thresholds = indifference_thresholds
    reinforced_preference_thresholds = reinforced_preference_thresholds
    reinforcement_factors = reinforcement_factors
    if profiles_performance is not None:
        categories_profiles = profiles_performance.keys()
        profile_performance_table = pc.directed_alternatives_performances(profiles_performance, directions)
    else:
        categories_profiles = None
        profile_performance_table = None
    decimal_place = decimal_place

    partialPref, Frp = _partial_preference(criteria, generalized_criteria, preference_thresholds,
                                           indifference_thresholds,
                                           reinforced_preference_thresholds, reinforcement_factors,
                                           alternatives_performances, profile_performance_table, categories_profiles)
    if categories_profiles is None:
        return _preferences(criteria, weights, reinforcement_factors, partialPref, decimal_place, Frp,
                            alternatives_performances), partialPref
    else:
        return (_preferences(criteria, weights, reinforcement_factors, partialPref[0], decimal_place, Frp[0],
                             alternatives_performances, profile_performance_table),
                _preferences(criteria, weights, reinforcement_factors, partialPref[1], decimal_place, Frp[1],
                             profile_performance_table, alternatives_performances)), partialPref


def _partial_preference(criteria: pd.Index, generalized_criteria: pd.Series, preference_thresholds: pd.Series,
                        indifference_thresholds: pd.Series, reinforced_preference_thresholds: pd.Series,
                        reinforcement_factors: pd.Series, alternatives_performances: PerformanceTable,
                        profile_performance_table: PerformanceTable, categories_profiles: pd.Index
                        ) -> tuple[pd.DataFrame, Union[List[List[List[List[int]]]], List[List[int]]]]:
    """
    Calculates partial preference of every alternative over others at every criterion
    based on deviations using a method chosen by user. If deviation is greater then
    reinforced preference threshold than partial preference takes the value of
    reinforcement factor.
    :return: partial preference indices
    """
    deviations = pc.deviations(criteria, alternatives_performances, profile_performance_table)
    if categories_profiles is None:
        ppIndices, Frp = _pp_deep(criteria, generalized_criteria, preference_thresholds, indifference_thresholds,
                                  reinforced_preference_thresholds, reinforcement_factors, deviations,
                                  alternatives_performances, alternatives_performances)
    else:

        ppIndices0, Frp0 = _pp_deep(criteria, generalized_criteria, preference_thresholds, indifference_thresholds,
                                    reinforced_preference_thresholds, reinforcement_factors, deviations[0],
                                    alternatives_performances, profile_performance_table)
        ppIndices1, Frp1 = _pp_deep(criteria, generalized_criteria, preference_thresholds, indifference_thresholds,
                                    reinforced_preference_thresholds, reinforcement_factors, deviations[1],
                                    profile_performance_table, alternatives_performances)
        ppIndices = [ppIndices0, ppIndices1]
        Frp = [Frp0, Frp1]

    return ppIndices, Frp


def _pp_deep(criteria: pd.Index, generalized_criteria: pd.Series, preference_thresholds: pd.Series,
             indifference_thresholds: pd.Series, reinforced_preference_thresholds: pd.Series,
             reinforcement_factors: pd.Series, deviations: List[List[List[NumericValue]]], i_iter: PerformanceTable,
             j_iter: PerformanceTable) -> tuple[pd.DataFrame, List[List[List[int]]]]:
    ppIndices = []
    FrpList = []
    for k in range(len(criteria)):
        method = generalized_criteria[k]
        q = indifference_thresholds[k]
        p = preference_thresholds[k]
        criterionIndices = []
        criterionFrp = []
        for i in range(i_iter.shape[0]):
            alternativeIndices = []
            alternativeFrp = []
            for j in range(j_iter.shape[0]):
                if deviations[k][i][j] > reinforced_preference_thresholds[criteria[k]]:
                    alternativeIndex = reinforcement_factors[criteria[k]]
                    Frp = 1
                else:
                    Frp = 0
                    if method is PreferenceFunction.USUAL:
                        alternativeIndex = gc.usual_criterion(deviations[k][i][j])
                    elif method is PreferenceFunction.U_SHAPE:
                        alternativeIndex = gc.u_shape_criterion(deviations[k][i][j], q)
                    elif method is PreferenceFunction.V_SHAPE:
                        alternativeIndex = gc.v_shape_criterion(deviations[k][i][j], p)
                    elif method is PreferenceFunction.LEVEL:
                        if q > p:
                            raise ValueError(
                                "incorrect threshold : q "
                                + str(q)
                                + " greater than p "
                                + str(p)
                            )
                        alternativeIndex = gc.level_criterion(deviations[k][i][j], p, q)
                    elif method is PreferenceFunction.V_SHAPE_INDIFFERENCE:
                        if q > p:
                            raise ValueError(
                                "incorrect threshold : q "
                                + str(q)
                                + " greater than p "
                                + str(p)
                            )
                        alternativeIndex = gc.v_shape_indifference_criterion(deviations[k][i][j], p, q)
                    else:
                        raise ValueError(
                            "pref_func "
                            + str(method)
                            + " is not known or forbidden."
                        )
                alternativeIndices.append(alternativeIndex)
                alternativeFrp.append(Frp)
            criterionIndices.append(alternativeIndices)
            criterionFrp.append(alternativeFrp)
        ppIndices.append(criterionIndices)
        FrpList.append(criterionFrp)

    names = ['criteria'] + i_iter.index.names
    ppIndices = pd.concat([pd.DataFrame(data=x, index=i_iter.index, columns=j_iter.index) for x in ppIndices],
                          keys=criteria, names=names)

    return ppIndices, FrpList


def _preferences(criteria: pd.Index, weights: pd.Series, reinforcement_factors: pd.Series, partialPref: pd.DataFrame,
                 decimal_place: int, Frp: Union[List[List[List[int]]], List[List[int]]], i_perf: PerformanceTable,
                 j_perf: PerformanceTable = None) -> pd.DataFrame:
    i_iter = i_perf.index
    if j_perf is None:
        j_iter = i_iter
    else:
        j_iter = j_perf.index
    preferences = []
    for i in range(len(i_iter)):
        aggregatedPI = []
        for j in range(len(j_iter)):
            Pi_A_B_nom = 0
            Pi_A_B_denom = 0
            for k in range(len(criteria)):
                Pi_A_B_nom += partialPref.loc[criteria[k], i_iter[i]][j_iter[j]] * weights[
                    criteria[k]]
                if Frp[k][i][j] == 1:
                    Pi_A_B_denom += weights[criteria[k]] * reinforcement_factors[criteria[k]]
                else:
                    Pi_A_B_denom += weights[criteria[k]]
            Pi_A_B = round(Pi_A_B_nom / Pi_A_B_denom, decimal_place)
            aggregatedPI.append(Pi_A_B)
        preferences.append(aggregatedPI)

    preferences = pd.DataFrame(data=preferences, columns=j_iter, index=i_iter)
    return preferences
