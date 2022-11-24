import pandas as pd
from typing import List, Union, Tuple
from enum import Enum
from core.enums import CompareProfiles, Direction
from core.input_validation.flow_input_validation import _check_flows
from core.input_validation.alternatives_profiles_input_validation import *

__all__ = ["alternatives_support_validation", "prom_sort_validation", "promethee_tri_validation",
           "flow_sort_i_validation"]


# M22
def _check_categories(categories: List[str]):
    if not isinstance(categories, List):
        raise ValueError("Categories should be passed as a List of string objects")

    for category in categories:
        if not isinstance(category, str):
            raise ValueError("Category should be a string")


def _check_assignments(assignments: List[pd.DataFrame], categories: List[str]):
    if not isinstance(assignments, List):
        raise ValueError("Assignments should be passed as a List of DataFrame objects")

    for assignment in assignments:
        if not isinstance(assignment, pd.DataFrame):
            raise ValueError("Each assignment of DM should be passed as a DataFrame object")

        columns = assignment.columns.values.tolist()

        if 'worse' not in columns or 'better' not in columns:
            raise ValueError("Columns of DataFrame with assignments should be named worse and better")

        for worse_cat, better_cat in zip(assignment['worse'], assignment['better']):
            if worse_cat not in categories or better_cat not in categories:
                raise ValueError("Alternative can not be assign to category that does not exist in categories List")


def alternatives_support_validation(categories: List[str], assignments: List[pd.DataFrame]):
    _check_categories(categories)
    _check_assignments(assignments, categories)


def _check_thresholds(thresholds: pd.Series, criteria_num: int):
    if not isinstance(thresholds, pd.Series):
        raise ValueError("Criteria thresholds should be passed as a Series object")

    if len(thresholds) != criteria_num:
        raise ValueError("Number of thresholds should be equals to number of criteria")

    for threshold in thresholds:
        if not isinstance(threshold, (int, float)):
            raise ValueError("Threshold should be a numeric values")


def _check_category_profiles(category_profiles: pd.DataFrame):
    if not isinstance(category_profiles, pd.DataFrame):
        raise ValueError("Category profiles should be passed as a DataFrame object")

    if category_profiles.dtypes.values.all() not in ['float64', 'int64']:
        raise ValueError("Category profiles performance be a numeric value")

    # for criterion in criteria:
    #     for profile_per in category_profiles[criterion]:
    #         if not isinstance(profile_per, (int, float)):
    #             raise ValueError("Category profiles performance be a numeric value")


def _check_criteria_directions(criteria_directions: pd.Series):
    if not isinstance(criteria_directions, pd.Series):
        raise ValueError("Criteria directions should be passed as a Series object")

    if criteria_directions.any() not in [Direction.MAX, Direction.MIN] and \
            criteria_directions.values.any() not in [0, 1]:
        raise ValueError("Criteria directions should Direction enums from core.enums")

    # for direction in criteria_directions:
    #     if not isinstance(direction, (int, float)):
    #         raise ValueError("Criteria direction should be a numeric values")


def _check_cut_point(cut_point: Union[int, float]):
    if not isinstance(cut_point, (int, float)):
        raise ValueError("Cut point parameter should be passed a numeric values")


def _check_assign_to_better(assign_to_better: bool):
    if not isinstance(assign_to_better, bool):
        raise ValueError("Assign to better class parameter should have value True or False")


# M17
def prom_sort_validation(categories: List[str],
                         alternatives_flows: pd.DataFrame,
                         category_profiles_flows: pd.DataFrame,
                         criteria_thresholds: pd.Series,
                         category_profiles: pd.DataFrame,
                         criteria_directions: pd.Series,
                         cut_point: Union[int, float],
                         assign_to_better_class: bool = True):
    criteria_from_df = category_profiles.columns.unique().tolist()

    _check_categories(categories)
    _check_flows(alternatives_flows)
    _check_flows(category_profiles_flows)
    _check_thresholds(criteria_thresholds, len(criteria_from_df))
    _check_category_profiles(category_profiles)
    _check_criteria_directions(criteria_directions)
    _check_cut_point(cut_point)
    _check_assign_to_better(assign_to_better_class)


def _check_marginal_val(use_marginal_val: bool):
    if not isinstance(use_marginal_val, bool):
        raise ValueError("Use marginal value parameter should have value True or False")


def _check_alternative_partial_pref(alternatives_partial_preferences: Tuple[pd.DataFrame, pd.DataFrame]):
    if not isinstance(alternatives_partial_preferences, tuple):
        raise ValueError("Alternatives partial preferences should be passed as Tuple with 2 DataFrames with partial "
                         "preferences (alternatives vs profiles) and (profiles vs alternatives)")

    if not isinstance(alternatives_partial_preferences[0], pd.DataFrame) or not \
            isinstance(alternatives_partial_preferences[1], pd.DataFrame):
        raise ValueError("Partial preferences should be passed as a DataFrame object")


# M18
def promethee_tri_validation(categories: List[str],
                             criteria_weights: pd.Series,
                             alternatives_partial_preferences: Tuple[pd.DataFrame, pd.DataFrame],
                             profiles_partial_preferences: pd.DataFrame,
                             assign_to_better_class: bool = True,
                             use_marginal_value: bool = True):
    criteria_from_df = alternatives_partial_preferences[0].index.get_level_values(0).unique()

    _check_categories(categories)
    _check_weights(criteria_weights, len(criteria_from_df))
    _check_alternative_partial_pref(alternatives_partial_preferences)
    _check_partial_preferences(profiles_partial_preferences)
    _check_assign_to_better(assign_to_better_class)
    _check_marginal_val(use_marginal_value)


def _check_enum(profiles: Enum):
    if profiles is CompareProfiles.LIMITING_PROFILES:
        pass
    elif profiles is CompareProfiles.BOUNDARY_PROFILES:
        pass
    elif profiles is CompareProfiles.CENTRAL_PROFILES:
        pass
    else:
        raise ValueError(f"Incorrect profiles type: {profiles}")


# M19
def flow_sort_i_validation(categories: List[str],
                           category_profiles: pd.DataFrame,
                           criteria_directions: pd.Series,
                           alternatives_flows: pd.DataFrame,
                           category_profiles_flows: pd.DataFrame,
                           comparison_with_profiles: Enum):
    criteria_from_df = category_profiles.columns.unique().tolist()

    _check_categories(categories)
    _check_category_profiles(category_profiles)
    _check_criteria_directions(criteria_directions)
    _check_flows(alternatives_flows)
    _check_flows(category_profiles_flows)
    _check_enum(comparison_with_profiles)


def _check_compare_profiles_type_and_profiles_and_categories_length(compare_profiles: Enum,
                                                                    categories: List[str],
                                                                    category_profiles: pd.DataFrame):
    if compare_profiles is CompareProfiles.LIMITING_PROFILES:
        if len(categories) != len(category_profiles) - 1:
            raise ValueError("Number of categories should be equals to number of limiting profiles minus 1")
    elif compare_profiles is CompareProfiles.BOUNDARY_PROFILES:
        if len(categories) != len(category_profiles) + 1:
            raise ValueError("Number of categories should be equals to number of boundary profiles plus 1")
    elif compare_profiles is CompareProfiles.CENTRAL_PROFILES:
        if len(categories) != len(category_profiles):
            raise ValueError("Number of categories should be equals to number of central profiles")


def _check_prometheeII_flows(prometheeII_flows: pd.DataFrame, category_profiles: pd.DataFrame):
    if not isinstance(prometheeII_flows, pd.DataFrame):
        raise ValueError("PrometheeII flows should be passed as a DataFrame object")
    if not isinstance(prometheeII_flows.index, pd.MultiIndex):
        raise ValueError("PrometheeII flows should be passed as a DataFrame with MultiIndex")

    if prometheeII_flows.columns.tolist() != ['positive', 'negative', 'net']:
        raise ValueError("PrometheeII flows should be passed as a DataFrame with columns: positive, negative, net")

    for index, prometheeII_alternative_flows in prometheeII_flows.groupby(level=0):
        if not len(prometheeII_alternative_flows) == len(category_profiles) + 1:
            raise ValueError(f"Number of alternative's group objects in PrometheeII flows should be equals to "
                             f"number of profiles in category profiles plus 1. Alternative's group {index} has "
                             f"{len(prometheeII_alternative_flows)} object")


def _check_if_criteria_are_the_same(checked_object: pd.DataFrame, criteria: pd.Index, checked_object_name: str):
    if not (checked_object.columns == criteria).all():
        raise ValueError(f"Criteria in {checked_object_name} should be the same as in every other object with criteria")


# M20
def flow_sort_ii_validation(categories: List[str],
                            category_profiles: pd.DataFrame,
                            criteria_directions: pd.Series,
                            prometheeII_flows: pd.DataFrame,
                            comparison_with_profiles: CompareProfiles):
    _check_categories(categories)
    _check_category_profiles(category_profiles)
    _check_criteria_directions(criteria_directions)
    _check_prometheeII_flows(prometheeII_flows, category_profiles)
    _check_enum(comparison_with_profiles)
    _check_compare_profiles_type_and_profiles_and_categories_length(comparison_with_profiles, categories,
                                                                    category_profiles)
    _check_if_criteria_are_the_same(category_profiles, criteria_directions.index, "Profiles preferences")
