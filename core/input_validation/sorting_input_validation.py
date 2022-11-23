import pandas as pd
from typing import List

__all__ = ["alternatives_support_validation"]


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
