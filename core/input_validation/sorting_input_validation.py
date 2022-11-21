import pandas as pd
from typing import List, Union
from core.input_validation.ranking_input_validation import *

__all__ = ["alternatives_support_validation", "prom_sort_validation"]


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


def _check_category_profiles(category_profiles: pd.DataFrame, criteria: List[str]):
    if not isinstance(category_profiles, pd.DataFrame):
        raise ValueError("Category profiles should be passed as a DataFrame object")

    for criterion in criteria:
        for profile_per in category_profiles[criterion]:
            if not isinstance(profile_per, (int, float)):
                raise ValueError("Category profiles performance be a numeric value")


def _check_criteria_directions(criteria_directions: pd.Series):
    if not isinstance(criteria_directions, pd.Series):
        raise ValueError("Criteria directions should be passed as a Series object")

    for direction in criteria_directions:
        if not isinstance(direction, (int, float)):
            raise ValueError("Criteria direction should be a numeric values")


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
    _check_category_profiles(category_profiles, criteria_from_df)
    _check_criteria_directions(criteria_directions)
    _check_cut_point(cut_point)
    _check_assign_to_better(assign_to_better_class)
