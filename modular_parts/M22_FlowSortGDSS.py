"""
    .. image:: prometheePUT_figures/M22.jpg

    This module computes the assignments of given alternatives to categories
     using FlowSort GDSS procedure.

    Implementation and naming conventions are taken from
    :cite:p:`LoliiIshizakaGamberiniRiminiMessori2015`.
"""
import math
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from core.enums import CompareProfiles
from core.input_validation.sorting import flow_sort_gdss_validation
from core.preference_commons import directed_alternatives_performances
from core.promethee_check_dominance import check_dominance_condition_GDSS

__all__ = ["calculate_flowsort_gdss_sorted_alternatives"]


def _classify_alternative(
    categories: List[str],
    classification: pd.DataFrame,
    not_classified: Dict[str, Dict[str, pd.Index]],
    alternative_assignment: pd.Series,
):
    """
    Classify imprecisely alternative to proper category. Used in first step of
     assignment.

    :param categories: List with categories names as strings
    :param classification: pd.DataFrame with alternatives as index and 'worse'
        and 'better' columns. Contains imprecise assignments of alternatives
        to categories. Used to update imprecise assignments. This DataFrame is
        modified in place.
    :param not_classified: Dictionary with alternatives as keys and
        Dictionary with 'worse_category_voters' and
        'better_category_voters' as values. Contains alternatives which are
        not precisely classified yet and list of DMs who voted on particular
        category. Used to update not_classified. This Dictionary is modified
        in place.
    :param alternative_assignment: pd.Series with DMs as index and
        assignments of the current alternative as values. It contains
        assignment name as name of pd.Series.
    """

    # Get if all assignments are the same
    if alternative_assignment.nunique() > 1:
        # Case when assignments are different

        # Specify worse and better category
        worse_category, better_category = sorted(
            alternative_assignment.unique(), key=lambda x: categories.index(x)
        )

        # Get DMs names who voted for worse and better category
        DMs_that_chose_worse_category = alternative_assignment[
            alternative_assignment == worse_category
        ].index
        DMs_that_chose_better_category = alternative_assignment[
            alternative_assignment == better_category
        ].index

        # Update not_classified dictionary
        not_classified[str(alternative_assignment.name)] = {
            "worse_category_voters": DMs_that_chose_worse_category,
            "better_category_voters": DMs_that_chose_better_category,
        }

        # Update classification DataFrame
        classification.loc[alternative_assignment.name, "worse"] = worse_category
        classification.loc[alternative_assignment.name, "better"] = better_category
    else:
        # Case when assignments are the same

        # Update classification DataFrame by adding alternative with
        # the same worse and better category (precise assignment)
        classification.loc[
            alternative_assignment.name, "worse"
        ] = alternative_assignment.unique()[0]
        classification.loc[
            alternative_assignment.name, "better"
        ] = alternative_assignment.unique()[0]


def _calculate_first_step_assignments(
    alternatives: pd.Index,
    dms: pd.Index,
    alternatives_general_net_flows: pd.Series,
    profiles: pd.Index,
    profiles_general_net_flows: pd.DataFrame,
    categories: List[str],
    comparison_with_profiles: CompareProfiles,
) -> Tuple[pd.DataFrame, Dict[str, Dict[str, pd.Index]]]:
    """
    Use first step of assignment of FlowSort GDSS method to classify
    alternatives.
    Calculate assignment of each DM for each alternative. If alternative
    assignment is not unanimous adds this
    alternative to not_classified (precisely) list.

    :param alternatives: pd.Index with alternatives names as strings
    :param dms: pd.Index with DMs names as strings
    :param alternatives_general_net_flows: pd.Series with alternatives as
        index and alternatives general net flows as values
    :param profiles: pd.Index with profiles names as strings
    :param profiles_general_net_flows: pd.DataFrame with
        MultiIndex(DMs, profiles) as index and alternatives as columns
    :param categories: List of categories names as strings
    :param comparison_with_profiles: CompareProfiles enum. Indicates if
        type of profiles used in sorting (boundary or central)

    :return: Tuple with pd.DataFrame with alternatives as index and
        'worse' and 'better' columns and Dictionary with alternatives as keys
        and Dictionary with 'worse_category_voters' and
        'better_category_voters' as values. The DataFrame contains imprecise
        assignments of alternatives to categories. The Dictionary contains
        alternatives which are not precisely classified yet and list of DMs who
        voted on particular category.
    """

    # Init classification DataFrame and not_classified Dictionary
    classification = pd.DataFrame(
        index=alternatives, columns=["worse", "better"], dtype=str
    )
    not_classified: Dict[str, Dict[str, pd.Index]] = {}

    # Iterate over alternatives general net flows (rows) and profiles general
    # net flows (columns) to get flow of current alternative and
    # profiles flows which can be compared with current alternative
    for (alternative, alternative_general_net_flow), (
        _,
        profiles_general_net_flows_for_alternative,
    ) in zip(
        alternatives_general_net_flows.items(),
        profiles_general_net_flows.items(),
    ):

        # Create Series with DMs as index and assignments of the current
        # alternative as values
        alternative_assignments = pd.Series(index=dms, dtype=str, name=alternative)

        # Iterate over DMs to obtain assignment of alternative by each DM
        for (
            DM,
            DM_profiles_general_net_flows_for_alternative,
        ) in profiles_general_net_flows_for_alternative.groupby(level=0):

            # Case when soring is done with boundary profiles
            # Main idea is to compare flows until profile flow is greater
            if comparison_with_profiles == CompareProfiles.BOUNDARY_PROFILES:
                for profile_i, profile_net_flow in enumerate(
                    DM_profiles_general_net_flows_for_alternative.values
                ):

                    # Edge case when first profile flow is
                    # better than alternative flow
                    if (
                        profile_i == 0
                        and alternative_general_net_flow <= profile_net_flow
                    ):
                        alternative_assignments[DM] = categories[0]
                        break
                    # Edge case when last profile flow is lower than
                    # alternative flow
                    elif (
                        profile_i == len(profiles) - 1
                        and alternative_general_net_flow > profile_net_flow
                    ):
                        alternative_assignments[DM] = categories[-1]
                        break
                    elif alternative_general_net_flow <= profile_net_flow:
                        alternative_assignments[DM] = categories[profile_i]
                        break
            # Case when soring is done with central profiles
            else:
                # Get profile position, which is closest to alternative flow
                category_pos = np.argmin(
                    np.abs(
                        DM_profiles_general_net_flows_for_alternative.values
                        - alternative_general_net_flow
                    )
                )
                alternative_assignments[DM] = categories[category_pos]

        # Update the DataFrame classification and not_classified dictionary
        # by analyzing the assignments of each DM
        _classify_alternative(
            categories, classification, not_classified, alternative_assignments
        )

    return classification, not_classified


def _calculate_final_assignments(
    alternatives_general_net_flows: pd.Series,
    profiles: pd.Index,
    profiles_general_net_flows: pd.DataFrame,
    categories: List[str],
    dms_weights: pd.Series,
    comparison_with_profiles: CompareProfiles,
    classification: pd.DataFrame,
    not_classified: Dict[str, Dict[str, pd.Index]],
    assign_to_better_class: bool = True,
) -> pd.Series:
    """
    Use final step of assignment to classify alternatives which could not be
    precisely classified in first step of assignment.
    Calculates distance to worse and better category based on DMs decision
     and DMs alternative profile net flows.
    Then classifies alternative to category which has smaller distance
    to profile of that category.
     If distances are the same, alternative is classified by using
     param 'assign_to_better_class'.

    :param alternatives_general_net_flows: pd.Series with alternatives as
        index and alternatives general net flows as values
    :param profiles: pd.Index with profiles names
    :param profiles_general_net_flows: pd.DataFrame with
        MultiIndex(DMs, profiles) as index and alternatives as columns
    :param categories: List of categories names as strings
    :param dms_weights: pd.Series with DMs as index and DMs weights as values
    :param comparison_with_profiles: CompareProfiles enum. Indicates if
        type of profiles used in sorting (boundary or central)
    :param classification: pd.DataFrame with alternatives as index and
        'worse' and 'better' columns. Contains imprecise assignments of
        alternatives to categories.
    :param not_classified: Dictionary with alternatives as keys
        and Dictionary with 'worse_category_voters' and
        'better_category_voters' as values. The Dictionary contains
        alternatives which are not precisely classified yet and list of DMs who
        voted on particular category.
    :param assign_to_better_class: bool. Indicates if alternative should be
        assigned to better category if distances to both categories are the
        same.

    :return: pd.Series with alternatives as index and final assignments as
        values.
    """

    # Init final assignments as DataFrame
    final_classification = classification.copy()

    # Iterate over alternatives which are not classified yet
    for alternative, voters in not_classified.items():

        # Extract DMs who voted for worse and better category
        worse_category_voters = pd.Index(voters["worse_category_voters"])
        better_category_voters = pd.Index(voters["better_category_voters"])

        # Get worse and better category names
        worse_category = classification.loc[alternative, "worse"]
        better_category = classification.loc[alternative, "better"]

        # Get weights of DMs who voted for worse category
        worse_category_voters_weights = dms_weights[worse_category_voters].unique()
        # Get name of worse category profile
        worse_category_profile = profiles[categories.index(worse_category)]

        # Get net flows of DMs who voted for worse category of profile
        # of worse category which are to be compared with alternative
        worse_category_profiles_general_net_flows = profiles_general_net_flows.loc[
            (worse_category_voters, worse_category_profile), alternative
        ]

        # Get weights of DMs who voted for better category
        better_category_voters_weights = dms_weights[better_category_voters].unique()
        # Get name of better category profile
        better_category_profile = profiles[
            min(categories.index(better_category), len(profiles) - 1)
        ]
        # Get net flows of DMs who voted for better category of profile
        # of better category which are to be compared with alternative
        better_category_profiles_general_net_flows = profiles_general_net_flows.loc[
            (better_category_voters, better_category_profile), alternative
        ]

        # Idea of precise sorting is to calculate 'distance' to worse and
        # better category based on mentioned profiles flows and
        # alternative flow

        # Case when soring is done with boundary profiles
        if comparison_with_profiles == CompareProfiles.BOUNDARY_PROFILES:
            worse_category_distance = np.sum(
                (
                    alternatives_general_net_flows[alternative]
                    - worse_category_profiles_general_net_flows
                )
                * worse_category_voters_weights
            )

            better_category_distance = np.sum(
                (
                    better_category_profiles_general_net_flows
                    - alternatives_general_net_flows[alternative]
                )
                * better_category_voters_weights
            )
        # Case when soring is done with central profiles
        else:
            worse_category_distance = np.sum(
                abs(
                    worse_category_profiles_general_net_flows
                    - alternatives_general_net_flows[alternative]
                )
                * worse_category_voters_weights
            )

            better_category_distance = np.sum(
                abs(
                    better_category_profiles_general_net_flows
                    - alternatives_general_net_flows[alternative]
                )
                * better_category_voters_weights
            )

        # Assign alternative to category which has smaller distance
        # to profile of that category
        # If distances are the same, alternative is classified by using
        # param 'assign_to_better_class'
        if math.isclose(
            worse_category_distance, better_category_distance, abs_tol=1e-6
        ):
            if assign_to_better_class:
                final_classification.loc[alternative, "final"] = better_category
            else:
                final_classification.loc[alternative, "final"] = worse_category
        elif better_category_distance > worse_category_distance:
            final_classification.loc[alternative, "better"] = worse_category
        else:  # better_category_distance < worse_category_distance:
            final_classification.loc[alternative, "better"] = better_category

    # Get final assignments
    return final_classification["better"]


def calculate_flowsort_gdss_sorted_alternatives(
    alternatives_general_net_flows: pd.Series,  # M12
    profiles_general_net_flows: pd.DataFrame,  # M12
    categories: List[str],
    criteria_directions: pd.Series,
    profiles_performances: List[pd.DataFrame],
    dms_weights: pd.Series,
    comparison_with_profiles: CompareProfiles,
    assign_to_better_class: bool = True,
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Sort alternatives to proper categories.

    :param alternatives_general_net_flows: pd.Series with alternatives and
        alternatives general net flows. Get from MultipleCriteriaNetFlows
        module.
    :param profiles_general_net_flows: pd.DataFrame with
        MultiIndex(DM, profile) and alternatives as columns
    :param categories: List of categories names as strings
    :param criteria_directions: pd.Series with criteria as index and
        Direction enums as values. Indicates if criterion has to be maximized
        or minimized.
    :param profiles_performances: pd.DataFrame with profiles as index
        and criteria as columns
    :param dms_weights: pd.Series with DMs as index and weights as values
    :param comparison_with_profiles: CompareProfiles enum. Indicates if
        type of profiles used in sorting (boundary or central)
    :param assign_to_better_class: Boolean, describe preference of
        the DMs in final alternative assignment when
        distances to worse and better class are equal.

    :return: Tuple with pd.DataFrame with alternatives as index
        and 'worse' and 'better' columns and pd.Series with alternatives as
        index and assignments as values. The DataFrame contains imprecise
        assignments and Series contains precise assignments.
    """

    # Input Validation
    flow_sort_gdss_validation(
        alternatives_general_net_flows,
        profiles_general_net_flows,
        categories,
        criteria_directions,
        profiles_performances,
        dms_weights,
        comparison_with_profiles,
        assign_to_better_class,
    )

    # Get alternatives, profiles and dms names
    alternatives = alternatives_general_net_flows.index
    profiles = profiles_performances[0].index
    dms = profiles_general_net_flows.index.get_level_values(0)

    # Multiply by -1 profiles performances on criteria which are
    # to be minimized. This is done to unify all criteria to be maximized.
    profiles_performances = [
        directed_alternatives_performances(
            single_DM_profiles_performances, criteria_directions
        )
        for single_DM_profiles_performances in profiles_performances
    ]

    # Check dominance condition
    check_dominance_condition_GDSS(profiles, profiles_performances, criteria_directions)

    # Calculate first classification (imprecise)
    first_step_assignments, not_classified = _calculate_first_step_assignments(
        alternatives,
        dms,
        alternatives_general_net_flows,
        profiles,
        profiles_general_net_flows,
        categories,
        comparison_with_profiles,
    )

    # Calculate final classification (precise)
    final_step_assignments = _calculate_final_assignments(
        alternatives_general_net_flows,
        profiles,
        profiles_general_net_flows,
        categories,
        dms_weights,
        comparison_with_profiles,
        first_step_assignments,
        not_classified,
        assign_to_better_class,
    )

    return first_step_assignments, final_step_assignments
