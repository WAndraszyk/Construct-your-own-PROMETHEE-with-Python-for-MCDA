from core.aliases import NumericValue, PerformanceTable
import core.preference_commons as pc
import pandas as pd

__all__ = ["compute_preference_indices"]


def compute_preference_indices(alternatives_performances: PerformanceTable, preference_thresholds: pd.Series,
                               indifference_thresholds: pd.Series, standard_deviations: pd.Series,
                               generalized_criteria: pd.Series,
                               directions: pd.Series, weights: pd.Series,
                               profiles_performance: PerformanceTable = None,
                               decimal_place: NumericValue = 3) -> tuple:
    """
    Calculates preference of every alternative over other alternatives
    or profiles based on partial preferences
    
    :param alternatives_performances: Dataframe of alternatives' value at every criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param standard_deviations: standard deviation for each criterion
    :param generalized_criteria: list of preference functions
    :param directions: directions of preference of criteria
    :param weights: criteria with weights
    :param profiles_performance: Dataframe of profiles performance (value) at every criterion
    :param decimal_place: with this you can choose the decimal_place of the output numbers

    :return: preferences
    :return: partial preferences
    """
    alternatives = alternatives_performances.index
    criteria = weights.keys()
    alternatives_performances = pc.directed_alternatives_performances(alternatives_performances, directions)
    if profiles_performance is not None:
        categories_profiles = profiles_performance.keys()
        profile_performance_table = pc.directed_alternatives_performances(profiles_performance, directions)
    else:
        categories_profiles = None
        profile_performance_table = None

    partialPref = pc.partial_preference(criteria=criteria, p_list=preference_thresholds,
                                        q_list=indifference_thresholds, s_list=standard_deviations,
                                        generalized_criteria=generalized_criteria,
                                        categories_profiles=categories_profiles,
                                        alternatives_performances=alternatives_performances,
                                        profile_performance_table=profile_performance_table)
    if categories_profiles is None:
        return _preferences(weights, criteria, decimal_place, partialPref, alternatives), partialPref
    else:
        return (_preferences(weights, criteria, decimal_place, partialPref[0], alternatives, categories_profiles),
                _preferences(weights, criteria, decimal_place, partialPref[1], categories_profiles, alternatives)
                ), partialPref


def _preferences(weights: pd.Series, criteria: pd.Index, decimal_place: NumericValue, partialPref: pd.DataFrame,
                 i_iter: pd.Index, j_iter: pd.Index = None) -> pd.DataFrame:
    weight_sum = sum(weights.values)
    if j_iter is None:
        j_iter = i_iter
    preferences = []
    for i in i_iter:
        aggregatedPI = []
        for j in j_iter:
            Pi_A_B = 0
            for k in criteria:
                Pi_A_B += partialPref.loc[k, i][j] * weights[k]
            Pi_A_B = Pi_A_B / weight_sum
            aggregatedPI.append(round(Pi_A_B, decimal_place))
        preferences.append(aggregatedPI)

    preferences = pd.DataFrame(data=preferences, columns=j_iter, index=i_iter)
    return preferences
