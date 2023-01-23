"""
.. image:: prometheePUT_figures/M6.jpg

This module implements a way of calculating discordance indices which
is a measure of the extent to which criterion j is discordant with aPjb using
Promethee Discordance method.

Implementation and naming of conventions are taken from
:cite:p:`Discordance`.
"""
from typing import List, Tuple, Union, cast

import pandas as pd

from core.input_validation.preference import discordance_validation
from core.preference_commons import overall_preference

__all__ = ["compute_discordance"]


def compute_discordance(
    criteria: List[str],
    partial_preferences: Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]],
    tau: float,
    decimal_place: int = 3,
    preferences: Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]] = None,
    were_categories_profiles: bool = False,
) -> Union[
    Tuple[
        Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]],
        Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]],
    ],
    Tuple[
        Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]],
        Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]],
        Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]],
    ],
]:
    """
    Calculates overall discordance by aggregating partial discordance indices.

    :param tau: technical parameter, τ ∈ [1, k], smaller τ → weaker
        discordance
    :param decimal_place: the decimal place of the output numbers
    :param preferences: DataFrame of preference indices as value,
        alternatives/profiles as index and columns,
        if not None function additionally returns calculated overall
        preference instead of just discordance
    :param criteria: list of criteria
    :param partial_preferences: DataFrame of partial preference indices as
        value, alternatives/profiles and criteria as index and
        alternatives/profiles as columns
    :param were_categories_profiles: were the preferences calculated
        for profiles

    :return: Tuple of DataFrame of overall discordance (alternatives/profiles
             as index and columns) and DataFrame of partial discordance
             indices (alternatives/profiles and criteria as index,
             alternatives/profiles as columns). With profiles, it's going to
             be Tuple of tuples of DataFrames of overall discordance and
             DataFrames of partial discordance indices. Additionally, if
             preferences given: DataFrame of overall preference
             (alternatives/profiles as index and columns) or tuple of
             DataFrames of overall preference with profiles.
    """
    # validate input data
    discordance_validation(
        criteria,
        partial_preferences,
        tau,
        decimal_place,
        preferences,
        were_categories_profiles,
    )

    partial_discordance: Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]
    discordance: Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]
    # check if partial preferences were calculated with profiles
    if not were_categories_profiles:
        partial_preferences = cast(pd.DataFrame, partial_preferences)
        # calculate partial_discordance and discordance
        partial_discordance = _calculate_partial_discordance(
            criteria, partial_preferences
        )
        discordance = _overall_discordance(
            criteria, partial_discordance, tau, decimal_place
        )
    else:
        partial_preferences = cast(
            Tuple[pd.DataFrame, pd.DataFrame], partial_preferences
        )
        # calculate partial discordance for both DataFrames in tuple
        partial_discordance = (
            _calculate_partial_discordance(
                criteria, partial_preferences[0], partial_preferences[1]
            ),
            _calculate_partial_discordance(
                criteria, partial_preferences[1], partial_preferences[0]
            ),
        )
        # calculate discordance for both partial discordances in the list
        discordance = (
            _overall_discordance(criteria, partial_discordance[0], tau, decimal_place),
            _overall_discordance(criteria, partial_discordance[1], tau, decimal_place),
        )

    # check whether to calculate overall preference
    if preferences is not None:
        return (
            discordance,
            partial_discordance,
            overall_preference(
                preferences,
                discordance,
                were_categories_profiles,
                decimal_place,
            ),
        )
    else:
        return discordance, partial_discordance


def _calculate_partial_discordance(
    criteria: List[str],
    partial_preferences: pd.DataFrame,
    other_partial_preferences: pd.DataFrame = None,
) -> pd.DataFrame:
    """
    Calculates partial discordance indices based on partial preference indices

    :param criteria: list of criteria
    :param partial_preferences: DataFrame of partial preference indices as
        value, alternatives/profiles and criteria as index and
        alternatives/profiles as columns
    :param other_partial_preferences: DataFrame of partial preference of
        every alternative over other alternatives or profiles or None

    :returns: DataFrame of partial discordance indices as value,
        alternatives/profiles and criteria as index and alternatives/profiles
        as columns
    """
    # check if there is a second partial preference DataFrame
    if other_partial_preferences is None:
        # if there is not, use the first one for both
        other_partial_preferences = partial_preferences

    partial_discordance_data = []

    for criterion in criteria:
        # calculate partial discordance for every criterion
        partial_discordance_on_criterion = other_partial_preferences.loc[criterion].T
        partial_discordance_data.append(partial_discordance_on_criterion)

    partial_discordance = pd.concat(partial_discordance_data, axis=0, keys=criteria)

    return partial_discordance


def _overall_discordance(
    criteria: List[str],
    partial_discordance: pd.DataFrame,
    tau: float,
    decimal_place: int,
) -> pd.DataFrame:
    """
    Calculates overall discordance by aggregating partial discordance indices.

    :param criteria: list of criteria names
    :param partial_discordance: DataFrame of partial discordance indices as
        1value, alternatives/profiles and criteria as index and
        alternatives/profiles as columns
    :param tau: technical parameter, τ ∈ [1, k], smaller τ → weaker
        discordance
    :param decimal_place: the decimal place of the output numbers

    :returns: DataFrame of discordance indices as value and
        alternatives/profiles as index and columns.
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
                    1 - min(partial_discordance.loc[criterion, i][column], 1),
                    tau / k,
                )
            D_a_b = 1 - D_a_b
            aggregated_discordance.append(round(D_a_b, decimal_place))
        discordance.append(aggregated_discordance)

    return pd.DataFrame(data=discordance, index=index, columns=columns)
