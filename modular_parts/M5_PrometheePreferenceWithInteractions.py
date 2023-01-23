"""
.. image:: prometheePUT_figures/M5.png

This module calculates preference indices with interactions between criteria.

Implementation and naming of conventions are taken from
:cite:p:`ElectreInteractions`.
"""

from typing import Tuple, Union, cast

import pandas as pd

import core.preference_commons as pc
from core.input_validation.preference import promethee_interaction_preference_validation

__all__ = ["compute_preference_indices_with_interactions"]


def compute_preference_indices_with_interactions(
    alternatives_performances: pd.DataFrame,
    weights: pd.Series,
    preference_thresholds: pd.Series,
    indifference_thresholds: pd.Series,
    s_parameters: pd.Series,
    generalized_criteria: pd.Series,
    directions: pd.Series,
    interactions: pd.DataFrame,
    profiles_performance: pd.DataFrame = None,
    decimal_place: int = 3,
    minimum_interaction_effect: bool = False,
) -> Union[
    Tuple[pd.DataFrame, pd.DataFrame],
    Tuple[
        Tuple[pd.DataFrame, pd.DataFrame],
        Tuple[pd.DataFrame, pd.DataFrame],
    ],
]:
    """
    Calculates preference of every alternative over other alternatives
    or profiles based on partial preferences. Includes
    interactions between criteria effect.

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
    :param interactions: DataFrame of interactions between criteria with
        coefficients, index: default , columns: criterion_1, criterion_2, type
        of interaction, coefficient
    :param profiles_performance: Dataframe of profiles performance (value) at
        every criterion, index: profiles, columns: criteria
    :param decimal_place: the decimal place of the output numbers
    :param minimum_interaction_effect: boolean representing function used to
        capture the interaction effects in the ambiguity zone. DM can choose 2
        different functions: minimum (true) or multiplication (false)
    :return: Tuple of preferences DataFrame (alternatives/profiles as index
        and columns) and partial preferences DataFrame (alternatives/profiles
        and criteria as index, alternatives/profiles as columns). With
        profiles, it's going to be Tuple of tuples of preferences DataFrames
        and partial preferences DataFrames.
    """
    # input data validation
    promethee_interaction_preference_validation(
        alternatives_performances,
        preference_thresholds,
        indifference_thresholds,
        s_parameters,
        generalized_criteria,
        directions,
        weights,
        profiles_performance,
        interactions,
        minimum_interaction_effect,
        decimal_place,
    )
    alternatives = alternatives_performances.index
    criteria = weights.index

    # changing values of alternatives' performances according to direction
    # of criterion for further calculations
    alternatives_performances = pc.directed_alternatives_performances(
        alternatives_performances, directions
    )

    # checking if profiles' performances were given
    categories_profiles: Union[pd.Index, None] = None
    profile_performance_table: Union[pd.DataFrame, None] = None
    if profiles_performance is not None:
        categories_profiles = profiles_performance.index
        # changing values of profiles' performances according to direction
        # of criterion for further calculations
        profile_performance_table = pc.directed_alternatives_performances(
            profiles_performance, directions
        )

    # calculating partial preference indices
    partial_pref = pc.partial_preference(
        criteria=criteria,
        preference_thresholds=preference_thresholds,
        indifference_thresholds=indifference_thresholds,
        s_parameters=s_parameters,
        generalized_criteria=generalized_criteria,
        categories_profiles=categories_profiles,
        alternatives_performances=alternatives_performances,
        profiles_performances=profile_performance_table,
    )

    # checking if categories_profiles exist
    if categories_profiles is None:
        # calculating preference indices for alternatives over alternatives
        partial_pref = cast(pd.DataFrame, partial_pref)
        return (
            cast(
                pd.DataFrame,
                _preferences(
                    minimum_interaction_effect,
                    interactions,
                    weights,
                    criteria,
                    partial_pref,
                    decimal_place,
                    alternatives,
                ),
            ),
            cast(pd.DataFrame, partial_pref),
        )
    else:
        # calculating preference indices for alternatives over profiles
        # and profiles over alternatives
        partial_pref = cast(Tuple[pd.DataFrame, pd.DataFrame], partial_pref)
        return (
            _preferences(
                minimum_interaction_effect,
                interactions,
                weights,
                criteria,
                partial_pref[0],
                decimal_place,
                alternatives,
                categories_profiles,
            ),
            _preferences(
                minimum_interaction_effect,
                interactions,
                weights,
                criteria,
                partial_pref[1],
                decimal_place,
                categories_profiles,
                alternatives,
            ),
        ), cast(Tuple[pd.DataFrame, pd.DataFrame], partial_pref)


def _preferences(
    minimum_interaction_effect: bool,
    interactions: pd.DataFrame,
    weights: pd.Series,
    criteria: pd.Index,
    partial_pref: pd.DataFrame,
    decimal_place: int,
    i_iter: pd.Index,
    j_iter: pd.Index = None,
) -> pd.DataFrame:
    """
    Calculates aggregated preference indices.

    :param minimum_interaction_effect: boolean representing function used to
        capture the interaction effects in the ambiguity zone.
    :param interactions: DataFrame of interactions between criteria with
        coefficients, index: default , columns: criterion_1, criterion_2, type
        of interaction, coefficient
    :param weights: Series with weights as values and criteria as index
    :param criteria: pd.Index with criteria indices
    :param partial_pref: DataFrame of partial preference indices as
        value, alternatives/profiles and criteria as index and
        alternatives/profiles as columns
    :param decimal_place: the decimal place of the output numbers
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
        aggregated_pi = []
        for j in j_iter:
            pi_a_b = 0.0
            interaction_ab = 0.0
            for k in criteria:
                pi_a_b += partial_pref.loc[k, i][j] * weights[k]

            # weights normalization
            pi_a_b /= weight_sum
            # calculating interaction effect for every interaction
            for key in interactions.index.values:
                k1 = interactions["criterion_1"].loc[key]
                k2 = interactions["criterion_2"].loc[key]
                coefficient = interactions["coefficient"].loc[key] * (
                    1 if interactions["type"].loc[key].value > 0 else -1
                )
                # if interaction's type is antagonistic
                if interactions["type"].loc[key].value == -1:
                    interaction_ab += (
                        _interaction_effects(
                            minimum_interaction_effect,
                            partial_pref.loc[k1, i][j],
                            partial_pref.loc[k2, j][i],
                        )
                        * coefficient
                    )
                # if interaction's type is strengthening or weakening
                else:
                    interaction_ab += (
                        _interaction_effects(
                            minimum_interaction_effect,
                            partial_pref.loc[k1, i][j],
                            partial_pref.loc[k2, i][j],
                        )
                        * coefficient
                    )
            # aggregate partial preference indices and interation effect
            # from each criterion

            # weights normalization, because for normal aggrageted preference
            # we made normalization earlier, instead of weight_sum we use 1
            aggregated = round(
                (pi_a_b + interaction_ab) / (1 + interaction_ab), decimal_place
            )
            aggregated_pi.append(aggregated if aggregated >= 0 else 0)
        preferences.append(aggregated_pi)
    return pd.DataFrame(data=preferences, columns=j_iter, index=i_iter)


def _interaction_effects(
    minimum_interaction_effect: bool, pi: float, pj: float
) -> float:
    """
    Calculates Function Z - used to capture the interaction effects in the
    ambiguity zone

    :param minimum_interaction_effect: boolean representing function used to
        capture the interaction effects in the ambiguity zone.
    :param pi: partial pref index
    :param pj: partial pref index
    :return: Numeric value, result of Z function used to capture the
        interaction effects in the ambiguity zone
    """
    if not minimum_interaction_effect:
        return pi * pj
    else:
        return min(pi, pj)
