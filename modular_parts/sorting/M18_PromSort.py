"""
    This module computes the assignments of given alternatives to
    categories using PromSort.

    Implementation and naming of conventions are taken from
    :cite:p:'ArazOzkarahan2007'.
"""
import math
import pandas as pd
from core.aliases import NumericValue
from typing import List, Tuple
from core.preference_commons import directed_alternatives_performances
from core.promethee_check_dominance import \
    check_if_profiles_are_strictly_worse
from core.input_validation import prom_sort_validation

__all__ = ["calculate_promsort_sorted_alternatives"]


def _define_outranking_relation(positive_flow_a: NumericValue,
                                negative_flow_a: NumericValue,
                                positive_flow_b: NumericValue,
                                negative_flow_b: NumericValue) -> chr:
    """
    This function declare 3 types of outranking relation between alternative
    and profile or profile and alternative (preference - 'P', indifference -
     'I', incomparable - '?')

    :param positive_flow_a: NumericValue that determines positive flow of
    first profile/alternative
    :param negative_flow_a: NumericValue that determines negative flow of
    first profile/alternative
    :param positive_flow_b: NumericValue that determines positive flow of
    second profile/alternative
    :param negative_flow_b: NumericValue that determines negative flow of
    second profile/alternative

    :return: chr that determines one of three types of outranking relation
    between first profile/alternative and second profile/alternative
    """
    if math.isclose(positive_flow_a, positive_flow_b) \
            and math.isclose(negative_flow_a, negative_flow_b):
        return "I"
    elif positive_flow_a >= positive_flow_b \
            and negative_flow_a <= negative_flow_b:
        return "P"
    elif (positive_flow_a > positive_flow_b and negative_flow_a >
          negative_flow_b) or \
            (positive_flow_a < positive_flow_b and negative_flow_a <
             negative_flow_b):
        return "R"
    else:
        return "?"


def _check_if_all_profiles_are_preferred_to_alternative(
        category_profiles_flows: pd.DataFrame,
        alternative_positive_flow: NumericValue,
        alternative_negative_flow: NumericValue) -> bool:
    """
    This function checks if all profiles are preferred to alternative
    (which allow sorting method to assign alternative to the worst category)

    :param category_profiles_flows: pd.DataFrame with alternatives as
    index and flows as columns named (positive and negative)
    :param alternative_positive_flow: NumericValue that determines positive
    flow of alternative
    :param alternative_negative_flow: NumericValue that determines negative
    flow of alternative

    :return: Boolean that determines if all profiles are preferred
    to alternative
    """
    outranking_relations = category_profiles_flows.apply(
        lambda row: _define_outranking_relation(row['positive'],
                                                row['negative'],
                                                alternative_positive_flow,
                                                alternative_negative_flow),
        axis=1)
    return outranking_relations.str.contains('P').all()


def _calculate_first_step_assignments(categories: List[str],
                                      alternatives_flows: pd.DataFrame,
                                      category_profiles_flows: pd.DataFrame
                                      ) -> pd.DataFrame:
    """
    This function calculates outranking relations alternative to each boundary
    profile, then:
    - if alternative is preferred to all boundary profiles then assign
     alternative to the best category
    - calculate outranking relations of each boundary profile to alternative,
     if all boundary profiles are
    preferred to alternative then assign alternative to the worst category
    - if first incomparable or indifference appeared to the worse profile
    than first preference then assign
    alternative to first preference index + 1 category
    - else alternative is "not fully classified". This alternative will have
     assigned first incomparable
    or indifference index category as worse class and first incomparable
    or indifference index +1 category
    as better class.

    :param categories: List with categories names as strings
    :param alternatives_flows: pd.DataFrame with alternatives as
    index and flows as columns named (positive and negative)
    :param category_profiles_flows: pd.DataFrame with alternatives as
    index and flows as columns named (positive and negative)

    :return: pd.DataFrame with alternatives names as index and
    assignments as columns named (worse and better)
    """

    classification = {alternative: [] for alternative in
                      alternatives_flows.index}

    category_profiles = category_profiles_flows.index

    for alternative, alternative_row in alternatives_flows.iterrows():
        outranking_relations = category_profiles_flows.apply(
            lambda category_profile_row: _define_outranking_relation(
                alternative_row['positive'], alternative_row['negative'],
                category_profile_row['positive'],
                category_profile_row['negative']), axis=1)

        # Checking alternatives outranking relations
        first_i_occurrence = category_profiles.get_loc(
            outranking_relations.str.contains('I').idxmax()) \
            if outranking_relations.str.contains('I').any() else float('inf')
        first_r_occurrence = category_profiles.get_loc(
            outranking_relations.str.contains('R').idxmax()) \
            if outranking_relations.str.contains('R').any() else float('inf')
        last_p_occurrence = category_profiles.get_loc(
            outranking_relations.str.contains('P').idxmin()) - 1 \
            if outranking_relations.str.contains('P').any() else float('inf')

        # Assignment conditions
        if outranking_relations[-1] == 'P':
            classification[alternative] = [categories[-1], categories[-1]]
        elif _check_if_all_profiles_are_preferred_to_alternative(
                category_profiles_flows, alternative_row['positive'],
                alternative_row['negative']):
            classification[alternative] = [categories[0], categories[0]]
        elif min(first_r_occurrence, first_i_occurrence) > last_p_occurrence:
            classification[alternative] = \
                [categories[last_p_occurrence + 1],
                 categories[last_p_occurrence + 1]]
        else:
            min_idx = min(first_r_occurrence, first_i_occurrence)
            classification[alternative] = [categories[min_idx],
                                           categories[min_idx + 1]]

    return pd.DataFrame.from_dict(classification, orient='index',
                                  columns=['worse', 'better'])


def _calculate_final_assignments(alternatives_flows: pd.DataFrame,
                                 category_profiles_flows: pd.DataFrame,
                                 classification: pd.DataFrame,
                                 cut_point: NumericValue,
                                 assign_to_better_class: bool = True
                                 ) -> pd.Series:
    """
    Used assigned categories to assign the unassigned ones. Based on
    positive and negative distance, that is calculated for each alternative,
    basing on calculated in first step categories (s and s+1).
    After calculating positive and negative distances a total distance
    is determining.
    After computing the total distance for all alternatives and profiles it is
    compared with cut point parameter.

    :param alternatives_flows: pd.DataFrame with alternatives as
    index and flows as columns named (positive and negative)
    :param category_profiles_flows: pd.DataFrame with profiles as
    index and flows as columns named (positive and negative)
    :param classification: pd.DataFrame with alternatives names as index and
    assignments as columns named (worse and better)
    :param cut_point: NumericValue in range <-1, 1> which define DM
    preference of classifying alternative to worse or better class in
    final alternative assignment
    :param assign_to_better_class: boolean which describe preference of
    the DM in final alternative assignment if total distance is equal
    cut_point value.

    :return: pd.Series objects with assignments as values
    """

    new_classification = classification.apply(
        lambda row: row['worse'] if row['worse'] == row['better'] else None,
        axis=1)
    not_classified = classification[new_classification.isnull()]
    classified = classification[~new_classification.isnull()]

    # Iterating over unassigned alternatives
    for alternative, alternative_row in not_classified.iterrows():
        worse_category_alternatives = alternatives_flows.loc[
            classified[classified['worse'] == alternative_row['worse']].index]
        better_category_alternatives = alternatives_flows.loc[
            classified[
                classified['worse'] == alternative_row['better']].index]

        alternative_net_outranking_flow = \
            alternatives_flows.loc[alternative, 'positive'] - \
            alternatives_flows.loc[alternative, 'negative']

        if worse_category_alternatives.empty:
            new_classification[alternative] = alternative_row['worse']
            continue
        else:
            worse_category_net_outranking_flow = \
                worse_category_alternatives.apply(
                    lambda row: row['positive'] - row['negative'], axis=1)
            positive_distance = \
                worse_category_net_outranking_flow.map(
                    lambda x: alternative_net_outranking_flow - x).sum() / \
                worse_category_alternatives.shape[0]

        if better_category_alternatives.empty:
            new_classification[alternative] = alternative_row['better']
            continue
        else:
            better_category_net_outranking_flow = \
                better_category_alternatives.apply(
                    lambda row: row['positive'] - row['negative'], axis=1)
            negative_distance = better_category_net_outranking_flow.map(
                lambda x: x - alternative_net_outranking_flow).sum() / \
                better_category_alternatives.shape[0]

        total_distance = positive_distance - negative_distance

        # Assignment based on distance comparison
        if total_distance > cut_point:
            new_classification[alternative] = alternative_row['better']
        elif total_distance < cut_point:
            new_classification[alternative] = alternative_row['worse']
        else:
            if assign_to_better_class:
                new_classification[alternative] = alternative_row['better']
            else:
                new_classification[alternative] = alternative_row['worse']

    return new_classification


def calculate_promsort_sorted_alternatives(
        categories: List[str],
        alternatives_flows: pd.DataFrame,
        category_profiles_flows: pd.DataFrame,
        criteria_thresholds: pd.Series,
        category_profiles: pd.DataFrame,
        criteria_directions: pd.Series,
        cut_point: NumericValue,
        assign_to_better_class: bool = True) -> \
        Tuple[pd.DataFrame, pd.Series]:
    """
    This function sorts alternatives to proper categories
    (based on PromSort).

    :param categories: List with categories names as strings
    :param alternatives_flows: pd.DataFrame with alternatives as
    index and flows as columns named (positive and negative)
    :param category_profiles_flows: pd.DataFrame with alternatives as
    index and flows as columns named (positive and negative)
    :param criteria_thresholds: pd.Series with criteria as index and
    thresholds as values
    :param category_profiles: pd.DataFrame with profiles as index and criteria
    as columns
    :param criteria_directions: pd.Series with criteria as index and
    Direction as values
    :param cut_point: NumericValue in range <-1, 1> which define DM
    preference of classifying alternative to worse or better class in
    final alternative assignment
    :param assign_to_better_class: Boolean which describe preference of
    the DM in final alternative assignment if total distance is equal
    cut_point value.
    :return: Tuple with pd.DataFrame with alternatives names as index and
    assignments as columns named (worse and better) and pd.Series objects with
    assignments as values
    """
    prom_sort_validation(categories, alternatives_flows,
                         category_profiles_flows, criteria_thresholds,
                         category_profiles, criteria_directions, cut_point,
                         assign_to_better_class)

    category_profiles = pd.DataFrame(
        directed_alternatives_performances(category_profiles,
                                           criteria_directions),
        index=category_profiles.columns, columns=category_profiles.columns)
    check_if_profiles_are_strictly_worse(criteria_thresholds,
                                         category_profiles)
    first_step_assignments = _calculate_first_step_assignments(
        categories,
        alternatives_flows,
        category_profiles_flows)

    final_step_assignments = _calculate_final_assignments(
        alternatives_flows,
        category_profiles_flows,
        first_step_assignments,
        cut_point,
        assign_to_better_class)

    return first_step_assignments, final_step_assignments
