"""
.. image:: prometheePUT_figures/M4.jpg

This module calculates preference indices with possibility of
reinforcement, which means giving a bonus to an alternative which is
significantly better on a given criterion than another alternative, using
Promethee Reinforced Preference method.

Implementation and naming of conventions are taken from
:cite:p:`ReinforcedPreference`.
"""
from typing import List, Optional, Tuple, Union, cast

import numpy as np
import pandas as pd

import core.generalized_criteria as gc
import core.preference_commons as pc
from core.input_validation.preference import reinforced_preference_validation
from core.preference_commons import GeneralCriterion

__all__ = ["compute_reinforced_preference"]


def compute_reinforced_preference(
    alternatives_performances: pd.DataFrame,
    preference_thresholds: pd.Series,
    indifference_thresholds: pd.Series,
    s_parameters: pd.Series,
    generalized_criteria: pd.Series,
    directions: pd.Series,
    reinforced_preference_thresholds: pd.Series,
    reinforcement_factors: pd.Series,
    weights: pd.Series,
    profiles_performance: pd.DataFrame = None,
    decimal_place: int = 3,
) -> Tuple[
    Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]],
    Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]],
]:
    """
    Calculates preference of every alternative over other alternatives
    or profiles based on partial preferences.
    Includes reinforced preference effect.

    :param alternatives_performances: Dataframe of alternatives' value at
        every criterion, index: alternatives, columns: criteria
    :param weights: Series with weights as values and criteria as index
    :param generalized_criteria: Series with preference functions as values
        and criteria as index
    :param preference_thresholds: Series of preference threshold for
        each criterion, index: criteria
    :param indifference_thresholds: Series of indifference threshold for
        each criterion, index: criteria
    :param s_parameters: Series of s parameter for each criterion, s parameter
        is a threshold used in Gaussian Criterion, it's defined as an
        intermediate value between indifference and preference threshold,
        index: criteria
    :param directions: Series with directions of preference as values and
        criteria as index
    :param reinforced_preference_thresholds: Series of reinforced preference
        thresholds for each criterion, index: criteria
    :param reinforcement_factors: Series of reinforcement factors
        for each criterion, index: criteria
    :param profiles_performance: Dataframe of profiles performance (value)
        at every criterion, index: profiles, columns: criteria
    :param decimal_place: the decimal place of the output numbers

    :return: Tuple of preferences DataFrame (alternatives/profiles as index
             and columns) and partial preferences DataFrame
             (alternatives/profiles and criteria as index,
             alternatives/profiles as columns). With profiles, it's going to
             be Tuple of tuples of preferences DataFrames and partial
             preferences DataFrames.
    """
    # input data validation
    reinforced_preference_validation(
        alternatives_performances,
        preference_thresholds,
        indifference_thresholds,
        generalized_criteria,
        directions,
        reinforced_preference_thresholds,
        reinforcement_factors,
        weights,
        profiles_performance,
        decimal_place,
    )

    criteria = weights.index

    # changing values of alternatives' performances according to direction
    # of criterion for further calculations
    alternatives_performances = pc.directed_alternatives_performances(
        alternatives_performances, directions
    )

    # checking if profiles' performances were given
    categories_profiles: Union[pd.Index, None]
    profile_performance_table: Union[pd.DataFrame, None]
    if profiles_performance is not None:
        categories_profiles = profiles_performance.index
        # changing values of profiles' performances according to direction
        # of criterion for further calculations
        profile_performance_table = pc.directed_alternatives_performances(
            profiles_performance, directions
        )
    else:
        categories_profiles = None
        profile_performance_table = None
    decimal_place = decimal_place

    # calculating partial preference indices
    partialPref, Frp = _partial_preference(
        criteria,
        generalized_criteria,
        preference_thresholds,
        indifference_thresholds,
        s_parameters,
        reinforced_preference_thresholds,
        reinforcement_factors,
        alternatives_performances,
        profile_performance_table,
        categories_profiles,
    )
    # checking if categories profiles exist
    if categories_profiles is None:
        # calculating preference indices for alternatives over alternatives
        Frp = cast(List[List[List[int]]], Frp)
        partialPref = cast(pd.DataFrame, partialPref)
        return (
            _preferences(
                criteria,
                weights,
                reinforcement_factors,
                partialPref,
                decimal_place,
                Frp,
                alternatives_performances.index,
            ),
            partialPref,
        )
    else:
        # calculating preference indices for alternatives over profiles
        # and profiles over alternatives
        partialPref = cast(Tuple[pd.DataFrame, pd.DataFrame], partialPref)
        Frp = cast(Tuple[List[List[List[int]]], List[List[List[int]]]], Frp)
        profile_performance_table = cast(pd.DataFrame, profile_performance_table)
        return (
            _preferences(
                criteria,
                weights,
                reinforcement_factors,
                partialPref[0],
                decimal_place,
                Frp[0],
                alternatives_performances.index,
                profile_performance_table.index,
            ),
            _preferences(
                criteria,
                weights,
                reinforcement_factors,
                partialPref[1],
                decimal_place,
                Frp[1],
                profile_performance_table.index,
                alternatives_performances.index,
            ),
        ), partialPref


def _partial_preference(
    criteria: pd.Index,
    generalized_criteria: pd.Series,
    preference_thresholds: pd.Series,
    indifference_thresholds: pd.Series,
    s_parameters: pd.Series,
    reinforced_preference_thresholds: pd.Series,
    reinforcement_factors: pd.Series,
    alternatives_performances: pd.DataFrame,
    profiles_performance: Optional[pd.DataFrame],
    categories_profiles: Optional[pd.Index],
) -> Tuple[
    Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]],
    Union[
        Tuple[List[List[List[int]]], List[List[List[int]]]],
        List[List[List[int]]],
    ],
]:
    """
    Calculates partial preference of every alternative over others
    at every criterion based on deviations using a method chosen by user.
    If deviation is greater than reinforced preference threshold than partial
    preference takes the value of reinforcement factor.

    :param criteria: list of criteria
    :param alternatives_performances: Dataframe of alternatives' value at
        every criterion
    :param generalized_criteria: Series with preference functions as values
        and criteria as index
    :param preference_thresholds: Series of preference threshold for
        each criterion, index: criteria
    :param indifference_thresholds: Series of indifference threshold for
        each criterion, index: criteria
    :param reinforced_preference_thresholds: Series of reinforced preference
        thresholds for each criterion, index: criteria
    :param reinforcement_factors: Series of reinforcement factors
        for each criterion, index: criteria
    :param profiles_performance: Dataframe of profiles performance (value)
        at every criterion, index: profiles, columns: criteria
    :param categories_profiles: list of categories profiles

    :return: DataFrame of partial preferences (alternatives/profiles and
        criteria as index, alternatives/profiles as columns). With profiles,
        it's going to be Tuple partial preferences DataFrames.
    """
    # calculate deviations
    deviations = pc.deviations(
        criteria, alternatives_performances, profiles_performance
    )

    # check if categories profiles were given
    ppIndices: Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]
    Frp: Union[
        Tuple[List[List[List[int]]], List[List[List[int]]]],
        List[List[List[int]]],
    ]
    if categories_profiles is None:
        # calculate partial preference indices
        deviations = cast(List[List[List[float]]], deviations)
        ppIndices, Frp = _pp_deep(
            criteria,
            generalized_criteria,
            preference_thresholds,
            indifference_thresholds,
            s_parameters,
            reinforced_preference_thresholds,
            reinforcement_factors,
            deviations,
            alternatives_performances,
            alternatives_performances,
        )
    else:
        # calculate partial preference indices
        deviations = cast(
            Tuple[List[List[List[float]]], List[List[List[float]]]], deviations
        )
        profiles_performance = cast(pd.DataFrame, profiles_performance)
        ppIndices0, Frp0 = _pp_deep(
            criteria,
            generalized_criteria,
            preference_thresholds,
            indifference_thresholds,
            s_parameters,
            reinforced_preference_thresholds,
            reinforcement_factors,
            deviations[0],
            alternatives_performances,
            profiles_performance,
        )
        ppIndices1, Frp1 = _pp_deep(
            criteria,
            generalized_criteria,
            preference_thresholds,
            indifference_thresholds,
            s_parameters,
            reinforced_preference_thresholds,
            reinforcement_factors,
            deviations[1],
            profiles_performance,
            alternatives_performances,
        )
        ppIndices = (ppIndices0, ppIndices1)
        Frp = (Frp0, Frp1)

    return ppIndices, Frp


def _pp_deep(
    criteria: pd.Index,
    generalized_criteria: pd.Series,
    preference_thresholds: pd.Series,
    indifference_thresholds: pd.Series,
    s_parameters: pd.Series,
    reinforced_preference_thresholds: pd.Series,
    reinforcement_factors: pd.Series,
    deviations: List[List[List[float]]],
    i_iter: pd.DataFrame,
    j_iter: pd.DataFrame,
) -> Tuple[pd.DataFrame, List[List[List[int]]]]:
    """
    This function computes the preference indices for a given set of
    alternatives and criteria.

    :param criteria: list of criteria
    :param preference_thresholds: Series of preference threshold for
        each criterion, index: criteria
    :param indifference_thresholds: Series of indifference threshold for
        each criterion, index: criteria
    :param s_parameters: Series of s parameter for each criterion, s parameter
        is a threshold used in Gaussian Criterion, it's defined as an
        intermediate value between indifference and preference threshold,
        index: criteria
    :param reinforced_preference_thresholds: Series of reinforced preference
        thresholds for each criterion, index: criteria
    :param reinforcement_factors: Series of reinforcement factors
        for each criterion, index: criteria
    :param generalized_criteria: Series with preference functions as values
        and criteria as index
    :param deviations: list of calculated deviations
    :param i_iter: alternatives or categories profiles performances
    :param j_iter: alternatives or categories profiles performances
        or None

    :return: DataFrame of partial preference indices as
        value, alternatives/profiles and criteria as index and
        alternatives/profiles as columns; 3D matrix of reinforced criteria.
    """
    # initialize partial preference indices matrix
    ppIndices = []
    # initialize reinforced criteria matrix
    FrpList = []
    for k in range(len(criteria)):
        method = generalized_criteria[k]
        q = indifference_thresholds[k]
        p = preference_thresholds[k]
        s = s_parameters[k]
        criterionIndices = []
        criterionFrp = []
        for i in range(i_iter.shape[0]):
            alternativeIndices = []
            alternativeFrp = []
            for j in range(j_iter.shape[0]):
                exceeds = False
                is_rp_none = True
                # check if there is a rp threshold
                if reinforced_preference_thresholds[criteria[k]].dtype in [
                    "int",
                    "int32",
                    "int64",
                    "float",
                    "float32",
                    "float64",
                ] and not np.isnan(reinforced_preference_thresholds[criteria[k]]):
                    is_rp_none = False
                    # check if deviation exceeds the rp threshold
                    exceeds = (
                        deviations[k][i][j]
                        > reinforced_preference_thresholds[criteria[k]]
                    )
                # if reinforced preference threshold exceeded:
                if exceeds:
                    # partial preference index takes value of reinforcement
                    # factor
                    alternativeIndex = reinforcement_factors[criteria[k]]
                    # mark criterion k as reinforced for preference between
                    # alternative i and j
                    Frp = 1
                else:
                    Frp = 0
                    # calculate partial preference index with chosen method
                    if method is GeneralCriterion.USUAL:
                        alternativeIndex = gc.usual_criterion(deviations[k][i][j])
                    elif method is GeneralCriterion.U_SHAPE:
                        alternativeIndex = gc.u_shape_criterion(deviations[k][i][j], q)
                    elif method is GeneralCriterion.V_SHAPE:
                        alternativeIndex = gc.v_shape_criterion(deviations[k][i][j], p)
                    elif method is GeneralCriterion.LEVEL:
                        if q > p:
                            raise ValueError(
                                "incorrect threshold : q "
                                + str(q)
                                + " greater than p "
                                + str(p)
                            )
                        alternativeIndex = gc.level_criterion(deviations[k][i][j], p, q)
                    elif method is GeneralCriterion.V_SHAPE_INDIFFERENCE:
                        if q > p:
                            raise ValueError(
                                "incorrect threshold : q "
                                + str(q)
                                + " greater than p "
                                + str(p)
                            )
                        alternativeIndex = gc.v_shape_indifference_criterion(
                            deviations[k][i][j], p, q
                        )
                    elif method is GeneralCriterion.GAUSSIAN and is_rp_none:
                        if s <= 0:
                            raise ValueError("s parameter should be grater than 0")
                        alternativeIndex = gc.gaussian_criterion(deviations[k][i][j], s)
                    else:
                        raise ValueError(
                            "pref_func " + str(method) + " is not known or forbidden."
                        )
                alternativeIndices.append(alternativeIndex)
                alternativeFrp.append(Frp)
            criterionIndices.append(alternativeIndices)
            criterionFrp.append(alternativeFrp)
        ppIndices.append(criterionIndices)
        FrpList.append(criterionFrp)

    names = ["criteria"] + i_iter.index.names
    ppIndices_df = pd.concat(
        [
            pd.DataFrame(data=x, index=i_iter.index, columns=j_iter.index)
            for x in ppIndices
        ],
        keys=criteria,
        names=names,
    )

    return ppIndices_df, FrpList


def _preferences(
    criteria: pd.Index,
    weights: pd.Series,
    reinforcement_factors: pd.Series,
    partialPref: pd.DataFrame,
    decimal_place: int,
    Frp: List[List[List[int]]],
    i_iter: pd.Index,
    j_iter: pd.Index = None,
) -> pd.DataFrame:
    """
    Calculates aggregated preference indices.

    :param weights: Series with weights as values and criteria as index
    :param criteria: list of criteria
    :param reinforcement_factors: list of reinforcement factors
    :param partialPref: DataFrame with partial preference indices as values,
        alternatives/profiles and criteria as indexes, alternatives/profiles
        as columns
    :param decimal_place: the decimal place of the output numbers
    :param Frp: 3D matrix of reinforced criteria.
        Frp[k][i][j] = 1 means that a reinforced preference occurs between
        alternative i and j on criterion k
    :param i_iter: alternatives or categories profiles
    :param j_iter: alternatives or categories profiles or None

    :return: DataFrame of aggregated preference indices as values,
        alternatives/profiles as index and columns.
    """
    # checking if second set of alternatives/profiles is given
    if j_iter is None:
        # if there is not, use the first one for both
        j_iter = i_iter

    preferences = []
    for i in range(len(i_iter)):
        aggregatedPI = []
        for j in range(len(j_iter)):
            Pi_A_B_nom = 0
            Pi_A_B_denom = 0
            # aggregate partial preference indices from each criterion
            for k in range(len(criteria)):
                Pi_A_B_nom += (
                    partialPref.loc[criteria[k], i_iter[i]][j_iter[j]]
                    * weights[criteria[k]]
                )
                # check if reinforcement occurs at criterion
                if Frp[k][i][j] == 1:
                    Pi_A_B_denom += (
                        weights[criteria[k]] * reinforcement_factors[criteria[k]]
                    )
                else:
                    Pi_A_B_denom += weights[criteria[k]]
            Pi_A_B = round(Pi_A_B_nom / Pi_A_B_denom, decimal_place)
            aggregatedPI.append(Pi_A_B)
        preferences.append(aggregatedPI)

    preferences_df = pd.DataFrame(data=preferences, columns=j_iter, index=i_iter)
    return preferences_df
