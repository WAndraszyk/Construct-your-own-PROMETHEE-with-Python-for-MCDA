"""
    This module computes the assignments of given alternatives to categories using FlowSort GDSS procedure.
"""
import pandas as pd
import numpy as np

from typing import List, Tuple, Dict
from core.enums import CompareProfiles
from core.input_validation.sorting_input_validation import flow_sort_gdss_validation
from core.preference_commons import directed_alternatives_performances
from core.promethee_check_dominance import check_dominance_condition_GDSS

__all__ = ["calculate_flowsort_gdss_sorted_alternatives"]


def _classify_alternative(categories: List[str], classification: pd.DataFrame,
                          not_classified: Dict[str, Dict[str, List[str]]], alternative_assignment: pd.Series):
    """
    Classify (or no) alternative to proper category. Used in first step of assignment.

    :param categories: List with categories names (strings only)
    :param classification: DataFrame with already done imprecise assignments (columns: 'worse', 'better')
    :param not_classified: Dictionary with alternatives which are not precisely classified yet
    :param alternative_assignment: Series with alternative assignment of each DM

    :return: Tuple with updated classification(DataFrame) and not_classified Dictionary
    """
    if alternative_assignment.nunique() > 1:
        worse_category, better_category = sorted(alternative_assignment.unique(),
                                                 key=lambda x: categories.index(x))

        DMs_that_chose_worse_category = alternative_assignment[alternative_assignment == worse_category].index
        DMs_that_chose_better_category = alternative_assignment[alternative_assignment == better_category].index

        not_classified[str(alternative_assignment.name)] = {'worse_category_voters': DMs_that_chose_worse_category,
                                                            'better_category_voters': DMs_that_chose_better_category}

        classification.loc[alternative_assignment.name, 'worse'] = worse_category
        classification.loc[alternative_assignment.name, 'better'] = better_category
    else:
        classification.loc[alternative_assignment.name, 'worse'] = alternative_assignment.unique()[0]
        classification.loc[alternative_assignment.name, 'better'] = alternative_assignment.unique()[0]

    return classification, not_classified


def _calculate_first_step_assignments(alternatives: pd.Index, dms: pd.Index, alternatives_general_net_flows: pd.Series,
                                      profiles: pd.Index, profiles_general_net_flows: pd.DataFrame,
                                      categories: List[str], comparison_with_profiles: CompareProfiles
                                      ) -> Tuple[pd.DataFrame, Dict[str, Dict[str, List[str]]]]:
    """
    Use first step of assignment of FlowSort GDSS method to classify alternatives.
    Calculate assignment of each DM for each alternative. If alternative assignment is not unanimous adds this
    alternative to not_classified list.

    :param alternatives: Index with alternatives names
    :param dms: Index with DM's names
    :param alternatives_general_net_flows: Series with alternatives general net flows
    :param profiles: Index with profiles names
    :param profiles_general_net_flows: DataFrame with profiles general net flows (index: (DM, profile),
     columns: alternatives)
    :param categories: List of categories names (strings only)
    :param comparison_with_profiles: Enum CompareProfiles - indicate information of profiles types used
    in calculation.

    :return: Tuple with imprecise classification DataFrame and not_classified Dictionary
    """

    classification = pd.DataFrame(index=alternatives, columns=['better', 'worse'], dtype=str)
    not_classified = {}

    for (alternative, alternative_general_net_flow), (_, profiles_general_net_flows_for_alternative) in zip(
            alternatives_general_net_flows.items(), profiles_general_net_flows.items()):
        alternative_assignments = pd.Series(index=dms, dtype=str, name=alternative)
        for DM, DM_profiles_general_net_flows_for_alternative in \
                profiles_general_net_flows_for_alternative.groupby(level=0):

            if comparison_with_profiles == CompareProfiles.BOUNDARY_PROFILES:
                for profile_i, profile_net_flow in enumerate(DM_profiles_general_net_flows_for_alternative.values):
                    if profile_i == 0 and alternative_general_net_flow <= profile_net_flow:
                        alternative_assignments[DM] = categories[0]
                        break
                    elif profile_i == len(profiles) - 1 and alternative_general_net_flow > profile_net_flow:
                        alternative_assignments[DM] = categories[-1]
                        break
                    elif alternative_general_net_flow <= profile_net_flow:
                        alternative_assignments[DM] = categories[profile_i]
                        break
            else:
                profile_distances = [profile_net_flow > alternative_general_net_flow for profile_net_flow in
                                     DM_profiles_general_net_flows_for_alternative.values]

                if profile_distances[-1]:
                    alternative_assignments[DM] = categories[-1]
                elif True in profile_distances:
                    category_index = profile_distances.index(True) + 1
                    alternative_assignments[DM] = categories[category_index]
                else:
                    alternative_assignments[DM] = categories[0]

        classification, not_classified = _classify_alternative(categories, classification,
                                                               not_classified, alternative_assignments)
    return classification, not_classified


def _calculate_final_assignments(alternatives_general_net_flows: pd.Series,
                                 profiles: pd.Index,
                                 profiles_general_net_flows: pd.DataFrame,
                                 categories: List[str],
                                 dms_weights: pd.Series,
                                 comparison_with_profiles: CompareProfiles,
                                 classification: pd.DataFrame,
                                 not_classified: Dict[str, Dict[str, List[str]]],
                                 assign_to_better_class: bool = True):
    """
    Use final step of assignment to classify alternatives which could not be classified in first step of assignment.
    Calculates distance to worse and better category based on DM's decision and DM's alternative profile net flows.
    Then classifies alternative to category which has smaller distance to it. If distances are the same,
    alternative is classified by using class param 'assign_to_better_class'.

    :param alternatives_general_net_flows: Series with alternatives general net flows
    :param profiles: Index with profiles names
    :param profiles_general_net_flows: DataFrame with profiles general net flows (index: (DM, profile),
     columns: alternatives)
    :param categories: List of categories names (strings only)
    :param dms_weights: Series with weight of each DM
    :param comparison_with_profiles: Enum CompareProfiles - indicate information of profiles types used
    in calculation.
    :param classification: DataFrame with imprecise assignments (columns: 'worse', 'better')
    :param not_classified: Dictionary with alternatives which are not precisely classified yet
    :param assign_to_better_class: Boolean which describe preference of the DMs in final alternative assignment when
    distances to worse and better class are equal.

    :return: Series with precise classification.
    """
    final_classification = classification.copy()

    for alternative, voters in not_classified.items():

        worse_category_voters = voters['worse_category_voters']
        better_category_voters = voters['better_category_voters']

        worse_category = classification.loc[alternative, 'worse']
        better_category = classification.loc[alternative, 'better']

        worse_category_voters_weights = dms_weights[worse_category_voters].unique()
        worse_category_profile = profiles[categories.index(worse_category)]
        worse_category_profiles_general_net_flows = \
            profiles_general_net_flows.loc[(worse_category_voters, worse_category_profile), alternative]

        better_category_voters_weights = dms_weights[better_category_voters].unique()
        better_category_profile = profiles[min(categories.index(
            better_category), len(profiles) - 1)]
        better_category_profiles_general_net_flows = \
            profiles_general_net_flows.loc[(better_category_voters, better_category_profile), alternative]

        if comparison_with_profiles == CompareProfiles.BOUNDARY_PROFILES:
            worse_category_distance = np.sum(
                (alternatives_general_net_flows[alternative] - worse_category_profiles_general_net_flows) *
                worse_category_voters_weights)

            better_category_distance = np.sum(
                (better_category_profiles_general_net_flows - alternatives_general_net_flows[alternative]) *
                better_category_voters_weights)

        else:
            worse_category_distance = np.sum(
                abs(worse_category_profiles_general_net_flows - alternatives_general_net_flows[alternative]) *
                worse_category_voters_weights)

            better_category_distance = np.sum(
                abs(better_category_profiles_general_net_flows - alternatives_general_net_flows[alternative]) *
                better_category_voters_weights)

        if better_category_distance > worse_category_distance:
            final_classification.loc[alternative, 'better'] = worse_category
        elif better_category_distance < worse_category_distance:
            final_classification.loc[alternative, 'better'] = better_category
        else:
            if assign_to_better_class:
                final_classification.loc[alternative, 'better'] = better_category
            else:
                final_classification.loc[alternative, 'better'] = worse_category

    final_classification = final_classification['better']

    return final_classification


def calculate_flowsort_gdss_sorted_alternatives(alternatives_general_net_flows: pd.Series,  # M21x
                                                profiles_general_net_flows: pd.DataFrame,  # M21x
                                                categories: List[str],
                                                criteria_directions: pd.Series,
                                                profiles_performances: List[pd.DataFrame],  # at least 2
                                                dms_weights: pd.Series,  # at least 2
                                                comparison_with_profiles: CompareProfiles,
                                                assign_to_better_class: bool = True) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Sort alternatives to proper categories.

    :param alternatives_general_net_flows: Series with alternatives general net flows
    :param profiles_general_net_flows: DataFrame with profiles general net flows (index: (DM, profile),
     columns: alternatives)
    :param categories: List of categories names (strings only)
    :param criteria_directions: Series with criteria directions (max or min)
    :param profiles_performances: List with DataFrames with profiles performances for each DM
    :param dms_weights: Series with weight of each DM
    :param comparison_with_profiles: Enum CompareProfiles - indicate information of profiles types used
    in calculation.
    :param assign_to_better_class: Boolean which describe preference of the DMs in final alternative assignment when
    distances to worse and better class are equal.

    :return: DataFrame with imprecise assignments (columns: 'worse', 'better') and Series with precise assignments.
    """
    flow_sort_gdss_validation(alternatives_general_net_flows, profiles_general_net_flows, categories,
                              criteria_directions, profiles_performances, dms_weights, comparison_with_profiles,
                              assign_to_better_class)

    alternatives = alternatives_general_net_flows.index
    categories = categories
    profiles = profiles_performances[0].index
    dms = profiles_general_net_flows.index.get_level_values(0)
    profiles_performances = [directed_alternatives_performances(
        single_DM_profiles_performances, criteria_directions)
        for single_DM_profiles_performances in profiles_performances]

    check_dominance_condition_GDSS(profiles, profiles_performances, criteria_directions)

    first_step_assignments, not_classified = \
        _calculate_first_step_assignments(alternatives, dms, alternatives_general_net_flows, profiles,
                                          profiles_general_net_flows, categories, comparison_with_profiles)
    final_step_assignments = _calculate_final_assignments(alternatives_general_net_flows, profiles,
                                                          profiles_general_net_flows, categories, dms_weights,
                                                          comparison_with_profiles, first_step_assignments,
                                                          not_classified, assign_to_better_class)

    return first_step_assignments, final_step_assignments
