"""
This module implements a way of calculating discordance indices which
is a measure of the extent to which criterion j is discordant with aPjb using
Promethee Discordance method.
"""
import pandas as pd
from typing import Tuple, List, Union
from core.aliases import NumericValue
from core.preference_commons import overall_preference
from core.input_validation import discordance_validation

__all__ = ["compute_discordance"]


def compute_discordance(criteria: List[str],
                        partial_preferences: Union[pd.DataFrame,
                                                   Tuple[pd.DataFrame]],
                        tau: NumericValue, decimal_place: NumericValue = 3,
                        preferences: Union[pd.DataFrame,
                                           Tuple[pd.DataFrame]] = None,
                        were_categories_profiles: bool = False
                        ) -> Union[
    Tuple[Union[pd.DataFrame, List[pd.DataFrame]], Union[
        pd.DataFrame, List[pd.DataFrame]]], pd.DataFrame, Tuple[
        pd.DataFrame]]:
    """
    Calculates overall discordance by aggregating partial discordance indices.

    :param tau: technical parameter, τ ∈ [1, k], smaller τ → weaker
        discordance
    :param decimal_place: the decimal place of the output numbers
    :param preferences: if not None function returns already calculated
        preference instead of just discordance
    :param criteria: list of criteria
    :param partial_preferences: partial preference of every alternative
        over other alternatives or profiles
    :param were_categories_profiles: were the preferences calculated
        for profiles

    :return: matrix of overall discordance and matrix of partial discordance
     indices. Alternatively: preference
    """
    # validate input data
    discordance_validation(criteria, partial_preferences, tau, decimal_place,
                           preferences, were_categories_profiles)

    # check if partial preferences were calculated with profiles
    if not were_categories_profiles:
        # calculate partial_discordance and discordance
        partial_discordance = _calculate_partial_discordance(
            criteria, partial_preferences)
        discordance = _overall_discordance(criteria, partial_discordance, tau,
                                           decimal_place)
    else:
        # calculate partial discordance for both DataFrames in tuple
        partial_discordance = [
            _calculate_partial_discordance(criteria, partial_preferences[0],
                                           partial_preferences[1]),
            _calculate_partial_discordance(criteria, partial_preferences[1],
                                           partial_preferences[0])]
        # calculate discordance for both partial discordances in the list
        discordance = []
        for i in partial_discordance:
            discordance.append(
                _overall_discordance(criteria, i, tau, decimal_place))

    # check whether to calculate overall preference
    if preferences is not None:
        return overall_preference(preferences, discordance,
                                  were_categories_profiles, decimal_place)
    else:
        return discordance, partial_discordance


def _calculate_partial_discordance(criteria: List[str],
                                   partial_preferences: pd.DataFrame,
                                   other_partial_preferences:
                                   pd.DataFrame = None) -> pd.DataFrame:
    """
    Calculates partial discordance indices based on partial preference indices

    :param criteria: list of criteria
    :param partial_preferences: partial preference of every alternative over 
        other alternatives or profiles
    :param other_partial_preferences: partial preference of every alternative 
        over other alternatives or profiles or None

    :returns: 3D matrix of partial discordance indices
    """
    # check if there is a second partial preference DataFrame
    if other_partial_preferences is None:
        # if there is not, use the first one for both
        other_partial_preferences = partial_preferences

    partial_discordance_data = []

    for criterion in criteria:
        # calculate partial discordance for every criterion
        partial_discordance_on_criterion = other_partial_preferences.loc[
            criterion].T
        partial_discordance_data.append(partial_discordance_on_criterion)

    partial_discordance = pd.concat(partial_discordance_data, axis=0,
                                    keys=criteria)

    return partial_discordance


def _overall_discordance(criteria: List[str],
                         partial_discordance: pd.DataFrame, tau: NumericValue,
                         decimal_place: NumericValue) -> pd.DataFrame:
    """
    Calculates overall discordance by aggregating partial discordance indices.

    :param criteria: list of criteria names
    :param partial_discordance: matrix of partial discordance indices
    :param tau: technical parameter, τ ∈ [1, k], smaller τ → weaker
     discordance
    :param decimal_place: with this you can choose the decimal_place of
     the output numbers
    :return: matrix of overall discordance
    """
    discordance = []
    k = len(criteria)
    index = partial_discordance.loc[criteria[0]].index
    columns = partial_discordance.loc[criteria[0]].columns
    for i in index:
        aggregated_discordance = []
        for column in columns:
            D_a_b = 1
            # aggregate partial discordance indices from each criterion
            for criterion in criteria:
                D_a_b *= pow(
                    1 - partial_discordance.loc[criterion, i][column],
                    tau / k)
            D_a_b = 1 - D_a_b
            aggregated_discordance.append(round(D_a_b, decimal_place))
        discordance.append(aggregated_discordance)

    return pd.DataFrame(data=discordance, index=index, columns=columns)
