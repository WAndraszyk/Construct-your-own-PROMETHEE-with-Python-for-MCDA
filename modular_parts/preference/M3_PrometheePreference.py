"""
This module implements the basic way of calculating preference indices with
Promethee Preference method.

Implementation and naming of conventions are taken from
:cite:p:'BransMareschal2005'.
"""
from typing import Tuple, Union

from core.aliases import NumericValue
import core.preference_commons as pc
from core.input_validation import promethee_preference_validation
import pandas as pd

__all__ = ["compute_preference_indices"]


def compute_preference_indices(alternatives_performances: pd.DataFrame,
                               preference_thresholds: pd.Series,
                               indifference_thresholds: pd.Series,
                               s_parameters: pd.Series,
                               generalized_criteria: pd.Series,
                               directions: pd.Series,
                               weights: pd.Series,
                               profiles_performance: pd.DataFrame = None,
                               decimal_place: NumericValue = 3
                               ) -> Tuple[
    Union[
        pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]],
    Union[
        pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]]:
    """
    Calculates preference of every alternative over other alternatives
    or profiles based on partial preferences.
    
    :param alternatives_performances: Dataframe of alternatives' value at
        every criterion, index: alternatives, columns: criteria
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
    :param directions: Series with directions of preference as values and
        criteria as index
    :param weights: Series with weights as values and criteria as index
    :param profiles_performance: Dataframe of profiles performance (value)
        at every criterion, index: profiles, columns: criteria
    :param decimal_place: the decimal place of the output numbers

    :return: Tuple of preferences DataFrame (alternatives/profiles as index
     and columns) and partial preferences DataFrame (alternatives/profiles and
     criteria as index, alternatives/profiles as columns). With profiles, it's
     going to be Tuple of tuples of preferences DataFrames and partial
     preferences DataFrames.
    """
    # input data validation
    promethee_preference_validation(alternatives_performances,
                                    preference_thresholds,
                                    indifference_thresholds,
                                    s_parameters,
                                    generalized_criteria, directions,
                                    weights, profiles_performance,
                                    decimal_place)

    alternatives = alternatives_performances.index
    criteria = weights.index

    # changing values of alternatives' performances according to direction
    # of criterion for further calculations
    alternatives_performances = pc.directed_alternatives_performances(
        alternatives_performances, directions)

    # checking if profiles' performances were given
    if profiles_performance is not None:
        categories_profiles = profiles_performance.index
        # changing values of profiles' performances according to direction
        # of criterion for further calculations
        profile_performance_table = pc.directed_alternatives_performances(
            profiles_performance, directions)
    else:
        categories_profiles = None
        profile_performance_table = None

    # calculating partial preference indices
    partialPref = pc.partial_preference(
        criteria=criteria,
        preference_thresholds=preference_thresholds,
        indifference_thresholds=indifference_thresholds,
        s_parameters=s_parameters,
        generalized_criteria=generalized_criteria,
        categories_profiles=categories_profiles,
        alternatives_performances=alternatives_performances,
        profiles_performances=profile_performance_table)
    # checking if categories profiles exist
    if categories_profiles is None:
        # calculating preference indices for alternatives over alternatives
        return _preferences(weights, criteria, decimal_place, partialPref,
                            alternatives), partialPref
    else:
        # calculating preference indices for alternatives over profiles
        # and profiles over alternatives
        return (_preferences(weights, criteria, decimal_place, partialPref[0],
                             alternatives, categories_profiles),
                _preferences(weights, criteria, decimal_place, partialPref[1],
                             categories_profiles, alternatives)
                ), partialPref


def _preferences(weights: pd.Series, criteria: pd.Index,
                 decimal_place: NumericValue, partialPref: pd.DataFrame,
                 i_iter: pd.Index, j_iter: pd.Index = None) -> pd.DataFrame:
    """
    Calculates aggregated preference indices.

    :param weights: Series with weights as values and criteria as index
    :param criteria: list of criteria
    :param decimal_place: the decimal place of the output numbers
    :param partialPref: DataFrame with partial preference indices as values,
        alternatives/profiles and criteria as indexes, alternatives/profiles
        as columns
    :param i_iter: alternatives or categories profiles
    :param j_iter: alternatives or categories profiles or None

    :return: DataFrame of aggregated preference indices as values,
        alternatives/profiles as index and columns.
    """
    # calculating sum of weights
    weight_sum = sum(weights.values)

    # checking if second set of alternatives/profiles is given
    if j_iter is None:
        # if there is not, use the first one for both
        j_iter = i_iter

    preferences = []
    for i in i_iter:
        aggregatedPI = []
        for j in j_iter:
            Pi_A_B = 0
            # aggregate partial preference indices from each criterion
            for k in criteria:
                Pi_A_B += partialPref.loc[k, i][j] * weights[k]
            Pi_A_B = Pi_A_B / weight_sum
            aggregatedPI.append(round(Pi_A_B, decimal_place))
        preferences.append(aggregatedPI)

    preferences = pd.DataFrame(data=preferences, columns=j_iter, index=i_iter)
    return preferences
