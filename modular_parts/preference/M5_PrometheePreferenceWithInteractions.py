from core.aliases import NumericValue, PerformanceTable
import core.preference_commons as pc
import pandas as pd

__all__ = ["compute_preference_indices_with_integrations"]

from core.input_validation import promethee_interaction_preference_validation


def compute_preference_indices_with_integrations(
        alternatives_performances: PerformanceTable,
        weights: pd.Series,
        preference_thresholds: pd.Series,
        indifference_thresholds: pd.Series,
        standard_deviations: pd.Series,
        generalized_criteria: pd.Series,
        directions: pd.Series,
        interactions: PerformanceTable,
        profiles_performance: PerformanceTable = None,
        decimal_place: NumericValue = 3,
        minimum_interaction_effect: bool = False) -> tuple:
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
    :param interactions: interactions between criteria with coefficient weight
    :param profiles_performance: Dataframe of profiles performance (value) at every criterion
    :param decimal_place: with this you can choose the decimal_place of the output numbers
    :param minimum_interaction_effect: function used to capture the interaction effects in the ambiguity zone. User can choose
    2 different functions: minimum or multiplication
    :return: preferences
    :return: partial preferences
    """
    promethee_interaction_preference_validation(alternatives_performances, preference_thresholds,
                                                indifference_thresholds, standard_deviations, generalized_criteria,
                                                directions, weights, profiles_performance,interactions, minimum_interaction_effect,decimal_place)
    alternatives = alternatives_performances.index
    criteria = weights.index
    alternatives_performances = pc.directed_alternatives_performances(alternatives_performances, directions)
    if profiles_performance is not None:
        categories_profiles = profiles_performance.index
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
        return _preferences(minimum_interaction_effect, interactions, weights, criteria, partialPref, decimal_place,
                            alternatives
                            ), partialPref
    else:
        return (_preferences(minimum_interaction_effect, interactions, weights, criteria, partialPref[0], decimal_place,
                             alternatives, categories_profiles),
                _preferences(minimum_interaction_effect, interactions, weights, criteria, partialPref[1], decimal_place,
                             categories_profiles, alternatives)
                ), partialPref


def _preferences(interaction_effects: NumericValue, interactions: PerformanceTable, weights: pd.Series,
                 criteria: pd.Index, partialPref: pd.Series, decimal_place: NumericValue, i_iter: pd.Index,
                 j_iter: pd.Index = None) -> pd.DataFrame:
    if j_iter is None:
        j_iter = i_iter
    preferences = []
    for i in i_iter:
        aggregatedPI = []
        for j in j_iter:
            Pi_A_B = 0
            interaction_ab = 0
            for k in criteria:
                Pi_A_B += partialPref.loc[k, i][j] * weights[k]
            for key in interactions.index.values:
                k1 = interactions['criterion_1'].loc[key]
                k2 = interactions['criterion_2'].loc[key]
                coefficient = interactions['coefficient'].loc[key] * (1 if interactions['type'].loc[key].value > 0 else -1)
                if interactions['type'].loc[key].value == -1:
                    interaction_ab += _interaction_effects(interaction_effects, partialPref.loc[k1, i][j],
                                                           partialPref.loc[k2, j][i]) * coefficient
                else:
                    interaction_ab += _interaction_effects(interaction_effects, partialPref.loc[k1, i][j],
                                                           partialPref.loc[k2, i][j]) * coefficient

            aggregated = round((Pi_A_B + interaction_ab) / (sum(weights.values) + interaction_ab), decimal_place)
            aggregatedPI.append(aggregated if aggregated >= 0 else 0)
        preferences.append(aggregatedPI)
    preferences = pd.DataFrame(data=preferences, columns=j_iter, index=i_iter)
    return preferences


def _interaction_effects(interaction_effects: NumericValue, pi: NumericValue, pj: NumericValue) -> NumericValue:
    if not interaction_effects:
        return pi * pj
    else:
        return min(pi, pj)
