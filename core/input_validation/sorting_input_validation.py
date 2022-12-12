import pandas as pd
from typing import List, Union, Tuple
from enum import Enum
from core.enums import CompareProfiles, Direction
from core.input_validation.flow_input_validation import _check_flows
from core.input_validation.alternatives_profiles_input_validation import *

__all__ = ["alternatives_support_validation", "prom_sort_validation",
           "promethee_tri_validation", "flow_sort_i_validation",
           "flow_sort_ii_validation", "flow_sort_gdss_validation",
           "multiple_dm_criteria_net_flows_validation"]


def _check_partial_preferences(partial_preferences: pd.DataFrame):
    """
    Check if partial preferences are valid.

    :param partial_preferences: pd.DataFrame with
    MultiIndex(criteria, alternatives) and columns as alternatives
    :raises ValueError: if partial preferences are not valid
    """

    # Check if partial preferences are a DataFrame
    if not isinstance(partial_preferences, pd.DataFrame):
        raise ValueError("Partial preferences should be passed"
                         " as a DataFrame object")


def _check_weights(weights: pd.Series, n_criteria: int):
    """
    Check if weights are valid.

    :param weights: pd.Series with criteria as index an weights as values
    :param n_criteria: number of criteria
    :raises ValueError: if weights are not valid
    """

    # Check if weights are a Series
    if not isinstance(weights, pd.Series):
        raise ValueError("Criteria weights should be passed as a"
                         " Series object")

    # Check if there are enough weights
    if len(weights) != n_criteria:
        raise ValueError("Number of weights should be equals "
                         "to number of criteria")

    # Check if weights are numeric
    if weights.dtype not in ['int32', 'int64', 'float32', 'float64']:
        raise ValueError("Weights should be a numeric values")

    # Check if all weights are positive
    if (weights <= 0).any():
        raise ValueError("Weights should be positive")


# M22
def _check_categories(categories: List[str]):
    if not isinstance(categories, List):
        raise ValueError("Categories should be passed as a "
                         "List of string objects")

    for category in categories:
        if not isinstance(category, str):
            raise ValueError("Category should be a string")


def _check_assignments(assignments: List[pd.DataFrame],
                       categories: List[str]):
    if not isinstance(assignments, List):
        raise ValueError("Assignments should be passed as a "
                         "List of DataFrame objects")

    for assignment in assignments:
        if not isinstance(assignment, pd.DataFrame):
            raise ValueError("Each assignment of DM should be "
                             "passed as a DataFrame object")

        columns = assignment.columns.values.tolist()

        if 'worse' not in columns or 'better' not in columns:
            raise ValueError("Columns of DataFrame with assignments"
                             " should be named worse and better")

        for worse_cat, better_cat in zip(assignment['worse'],
                                         assignment['better']):
            if worse_cat not in categories or better_cat not in categories:
                raise ValueError("Alternative can not be assign to category"
                                 " that does not exist in categories List")


def alternatives_support_validation(categories: List[str],
                                    assignments: List[pd.DataFrame]):
    _check_categories(categories)
    _check_assignments(assignments, categories)


def _check_thresholds(thresholds: pd.Series, criteria_num: int):
    if not isinstance(thresholds, pd.Series):
        raise ValueError("Criteria thresholds should be passed "
                         "as a Series object")

    if len(thresholds) != criteria_num:
        raise ValueError("Number of thresholds should be equals to"
                         " number of criteria")

    for threshold in thresholds:
        if not isinstance(threshold, (int, float)):
            raise ValueError("Threshold should be a numeric values")


def _check_category_profiles(category_profiles: pd.DataFrame):
    if not isinstance(category_profiles, pd.DataFrame):
        raise ValueError("Category profiles should be passed as a"
                         " DataFrame object")

    if category_profiles.dtypes.values.all() not in ['float64', 'int64']:
        raise ValueError("Category profiles performance be a numeric value")


def _check_criteria_directions(criteria_directions: pd.Series):
    if not isinstance(criteria_directions, pd.Series):
        raise ValueError("Criteria directions should be passed as "
                         "a Series object")

    if criteria_directions.values.any() not in [Direction.MAX, Direction.MIN]:
        raise ValueError("Criteria directions should Direction enums "
                         "from core.enums")


def _check_cut_point(cut_point: Union[int, float]):
    if not isinstance(cut_point, (int, float)):
        raise ValueError("Cut point parameter should be passed a"
                         " numeric values")


def _check_assign_to_better(assign_to_better: bool):
    if not isinstance(assign_to_better, bool):
        raise ValueError("Assign to better class parameter should"
                         " have value True or False")


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
        raise ValueError("Use marginal value parameter should "
                         "have value True or False")


def _check_alternative_partial_pref(
        alternatives_partial_preferences: Tuple[pd.DataFrame, pd.DataFrame]):
    if not isinstance(alternatives_partial_preferences, tuple):
        raise ValueError("Alternatives partial preferences should be"
                         " passed as Tuple with 2 DataFrames with partial "
                         "preferences (alternatives vs profiles) and "
                         "(profiles vs alternatives)")

    if not isinstance(alternatives_partial_preferences[0], pd.DataFrame) \
            or not isinstance(alternatives_partial_preferences[1],
                              pd.DataFrame):
        raise ValueError("Partial preferences should be passed as a"
                         " DataFrame object")


# M18
def promethee_tri_validation(categories: List[str],
                             criteria_weights: pd.Series,
                             alternatives_partial_preferences: Tuple[
                                 pd.DataFrame, pd.DataFrame],
                             profiles_partial_preferences: pd.DataFrame,
                             assign_to_better_class: bool = True,
                             use_marginal_value: bool = True):
    criteria_from_df = alternatives_partial_preferences[0].index. \
        get_level_values(0).unique()

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


def _check_compare_profiles_type_and_profiles_and_categories_length(
        compare_profiles: Enum,
        categories: List[str],
        category_profiles: pd.DataFrame,
        gdss: bool = False):
    if compare_profiles is CompareProfiles.LIMITING_PROFILES:
        if gdss:
            raise ValueError(
                "Limiting profiles are not available for FlowSortGDSS method")
        if len(categories) != len(category_profiles) - 1:
            raise ValueError(
                "Number of categories should be equals to number of "
                "limiting profiles minus 1")
    elif compare_profiles is CompareProfiles.BOUNDARY_PROFILES:
        if len(categories) != len(category_profiles) + 1:
            raise ValueError(
                "Number of categories should be equals to number of "
                "boundary profiles plus 1")
    elif compare_profiles is CompareProfiles.CENTRAL_PROFILES:
        if len(categories) != len(category_profiles):
            raise ValueError(
                "Number of categories should be equals to number of "
                "central profiles")


def _check_prometheeII_flows(prometheeII_flows: pd.DataFrame,
                             category_profiles: pd.DataFrame):
    if not isinstance(prometheeII_flows, pd.DataFrame):
        raise ValueError(
            "PrometheeII flows should be passed as a DataFrame object")
    if not isinstance(prometheeII_flows.index, pd.MultiIndex):
        raise ValueError(
            "PrometheeII flows should be passed as a DataFrame with "
            "MultiIndex")

    if prometheeII_flows.columns.tolist() != ['positive', 'negative', 'net']:
        raise ValueError(
            "PrometheeII flows should be passed as a DataFrame with "
            "columns: positive, negative, net")

    for index, prometheeII_alternative_flows in prometheeII_flows.groupby(
            level=0):
        if not len(prometheeII_alternative_flows) == len(
                category_profiles) + 1:
            raise ValueError(
                f"Number of alternative's group objects in PrometheeII"
                f" flows should be equals to "
                f"number of profiles in category profiles plus 1. "
                f"Alternative's group {index} has "
                f"{len(prometheeII_alternative_flows)} object")


def _check_if_criteria_are_the_same(checked_object: pd.DataFrame,
                                    criteria: pd.Index,
                                    checked_object_name: str):
    if not (checked_object.columns == criteria).all():
        raise ValueError(
            f"Criteria in {checked_object_name} should be the same "
            f"as in every other object with criteria")


def _check_net_flows(net_flows: pd.Series, checked_object_name: str):
    if not isinstance(net_flows, pd.Series):
        raise ValueError(
            f"{checked_object_name} should be passed as a Series object")

    if net_flows.dtype not in ['int64', 'float64']:
        raise ValueError(
            f"{checked_object_name} should be passed as a Series with"
            f" numeric values")


def _check_profiles_general_net_flows(
        profiles_general_net_flows: pd.DataFrame,
        alternatives_general_net_flows: pd.Series,
        profiles_performances: List[pd.DataFrame]):
    if not isinstance(profiles_general_net_flows, pd.DataFrame):
        raise ValueError(
            "Profiles general net flows should be passed as a "
            "DataFrame object")
    if not isinstance(profiles_general_net_flows.index, pd.MultiIndex):
        raise ValueError(
            "Profiles general net flows should be passed as a DataFrame "
            "with MultiIndex")

    if not (
            profiles_general_net_flows.columns ==
            alternatives_general_net_flows.index).all():
        raise ValueError(
            "Profiles general net flows should have columns equals to "
            "alternatives general net flows index")

    for index, profiles_general_net_flows_group in \
            profiles_general_net_flows.groupby(level=0):
        if not len(profiles_general_net_flows_group) == len(
                profiles_performances[0]):
            raise ValueError(
                f"Number of profiles in profiles general net flows should be"
                f" equals to "
                f"number of profiles in profiles performances. Profiles group"
                f" {index} has "
                f"{len(profiles_general_net_flows_group)} profiles")

    if profiles_general_net_flows.dtypes.values.all() not in ['float64',
                                                              'int64']:
        raise ValueError(
            "Profiles general net flows should be passed as a DataFrame "
            "with numeric values")

    for index, profiles_general_net_flow in \
            profiles_general_net_flows.groupby(level=0):
        if not len(profiles_general_net_flow) == len(
                profiles_general_net_flow.index.get_level_values(1).unique()):
            raise ValueError(
                f"Number of profiles in Profiles general net flows should be "
                f"equals to "
                f"number of alternatives in Profiles general net flows. "
                f"Profile {index} has "
                f"{len(profiles_general_net_flow)} alternatives")


def _check_profiles_performances_list(
        profiles_performances: List[pd.DataFrame]):
    if not isinstance(profiles_performances, list):
        raise ValueError(
            "Profiles performances should be passed as a list of DataFrames")

    if not all(isinstance(profiles_performance, pd.DataFrame) for
               profiles_performance in profiles_performances):
        raise ValueError(
            "Profiles performances should be passed as a list of DataFrames")

    if not all(len(profiles_performance) ==
               len(profiles_performances[0]) for profiles_performance in
               profiles_performances):
        raise ValueError(
            "Number of profiles in every profiles performances "
            "should be the same")

    if not all(len(profiles_performance.columns) == len(
            profiles_performances[0].columns)
               for profiles_performance in profiles_performances):
        raise ValueError(
            "Number of criteria in every profiles performances "
            "should be the same")

    if not all(
            profiles_performance.dtypes.values.all() in ['float64', 'int64']
            for profiles_performance in profiles_performances):
        raise ValueError(
            "Profiles performances should be passed as a list of "
            "DataFrames with numeric values")


def _check_dms_weights(dms_weights: pd.Series,
                       profiles_general_net_flows: pd.DataFrame):
    if not isinstance(dms_weights, pd.Series):
        raise ValueError("DMS weights should be passed as a Series object")

    if (dms_weights <= 0).any():
        raise ValueError("DMS weights should be positive")

    if not (
            dms_weights.index ==
            profiles_general_net_flows.index.get_level_values(
                0).unique()).all():
        raise ValueError(
            "DMS weights should have index equals to profiles"
            " general net flows index")


def _check_number_of_dms(profiles_general_net_flows: pd.DataFrame,
                         profiles_performances: List[pd.DataFrame],
                         dms_weights: pd.Series):
    if not len(profiles_performances) == len(dms_weights.index) == \
           len(profiles_general_net_flows.index.get_level_values(0).unique()):
        raise ValueError(
            "Number of DMs in profiles performances should be"
            " the same as in DMS weights and "
            "in profiles general net flows")


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
    _check_compare_profiles_type_and_profiles_and_categories_length(
        comparison_with_profiles, categories,
        category_profiles)
    _check_if_criteria_are_the_same(category_profiles,
                                    criteria_directions.index,
                                    "Profiles preferences")


# M21
def flow_sort_gdss_validation(alternatives_general_net_flows: pd.Series,
                              profiles_general_net_flows: pd.DataFrame,
                              categories: List[str],
                              criteria_directions: pd.Series,
                              profiles_performances: List[pd.DataFrame],
                              dms_weights: pd.Series,
                              comparison_with_profiles: CompareProfiles,
                              assign_to_better_class: bool = True):
    _check_net_flows(alternatives_general_net_flows,
                     "Alternatives general net flows")
    _check_profiles_general_net_flows(profiles_general_net_flows,
                                      alternatives_general_net_flows,
                                      profiles_performances)
    _check_categories(categories)
    _check_criteria_directions(criteria_directions)
    _check_profiles_performances_list(profiles_performances)
    _check_dms_weights(dms_weights, profiles_general_net_flows)
    _check_enum(comparison_with_profiles)
    _check_compare_profiles_type_and_profiles_and_categories_length(
        comparison_with_profiles, categories,
        profiles_performances[0], True)
    _check_assign_to_better(assign_to_better_class)


def _check_dms_profiles_partial_preferences(
        dms_profiles_partial_preferences: List[pd.DataFrame]):
    if not isinstance(dms_profiles_partial_preferences, list):
        raise ValueError(
            "DMs profiles partial preferences should be passed "
            "as a list of DataFrames")

    if not all(isinstance(dms_profiles_partial_preference, pd.DataFrame)
               for dms_profiles_partial_preference in
               dms_profiles_partial_preferences):
        raise ValueError(
            "DMs profiles partial preferences should be passed "
            "as a list of DataFrames")

    if not all(len(dms_profiles_partial_preference) ==
               len(dms_profiles_partial_preferences[0]) for
               dms_profiles_partial_preference in
               dms_profiles_partial_preferences):
        raise ValueError(
            "Number of profiles in every DMs profiles partial "
            "preferences should be the same")

    if not all(len(dms_profiles_partial_preference.columns) ==
               len(dms_profiles_partial_preferences[0].columns)
               for dms_profiles_partial_preference in
               dms_profiles_partial_preferences):
        raise ValueError(
            "Number of criteria in every DMs profiles partial "
            "preferences should be the same")

    if not all(
            dms_profiles_partial_preference.dtypes.values.all() in ['float64',
                                                                    'int64']
            for dms_profiles_partial_preference in
            dms_profiles_partial_preferences):
        raise ValueError(
            "DMs profiles partial preferences should be passed as "
            "a list of DataFrames with "
            "numeric values")


def _check_dms_alternatives_partial_preferences(
        dms_alternatives_partial_preferences: List[pd.DataFrame]):
    if not isinstance(dms_alternatives_partial_preferences, list):
        raise ValueError(
            "DMS alternatives partial preferences should be passed "
            "as a list of DataFrames")

    if not all(isinstance(dms_alternatives_partial_preference, pd.DataFrame)
               for dms_alternatives_partial_preference in
               dms_alternatives_partial_preferences):
        raise ValueError(
            "DMS alternatives partial preferences should be passed "
            "as a list of DataFrames")

    if not all(len(dms_alternatives_partial_preference) ==
               len(dms_alternatives_partial_preferences[0]) for
               dms_alternatives_partial_preference in
               dms_alternatives_partial_preferences):
        raise ValueError(
            "Number of alternatives in every DMs alternatives partial"
            " preferences should be the same")

    if not all(len(dms_alternatives_partial_preference.columns) ==
               len(dms_alternatives_partial_preferences[0].columns)
               for dms_alternatives_partial_preference in
               dms_alternatives_partial_preferences):
        raise ValueError(
            "Number of criteria in every DMS alternatives partial "
            "preferences should be the same")

    if not all(dms_alternatives_partial_preference.dtypes.values.all() in [
        'float64', 'int64']
               for dms_alternatives_partial_preference in
               dms_alternatives_partial_preferences):
        raise ValueError(
            "DMs alternatives partial preferences should be passed "
            "as a list of DataFrames with "
            "numeric values")


def _check_dms_profile_vs_profile_partial_preferences(
        dms_profile_vs_profile_partial_preferences: pd.DataFrame):
    if not isinstance(dms_profile_vs_profile_partial_preferences,
                      pd.DataFrame):
        raise ValueError(
            "DMs profile vs profile partial preferences "
            "should be passed as a DataFrame")

    number_of_criteria = len(
        dms_profile_vs_profile_partial_preferences.index.get_level_values(
            0).unique())
    columns_size = len(
        dms_profile_vs_profile_partial_preferences) / number_of_criteria

    if len(dms_profile_vs_profile_partial_preferences.columns) != \
            columns_size:
        raise ValueError(
            "DMs profile vs profile partial preferences should be passed "
            "as a DataFrame with "
            "number of columns equal to number of all profiles")

    if not (dms_profile_vs_profile_partial_preferences.index.droplevel(
            0).unique() ==
            dms_profile_vs_profile_partial_preferences.columns).all():
        raise ValueError(
            "DMs profile vs profile partial preferences should be passed"
            " as a DataFrame with "
            "identical index and columns")

    profiles_index = dms_profile_vs_profile_partial_preferences. \
        index.droplevel(0).unique()

    for index, profile_vs_profile_partial_preferences in \
            dms_profile_vs_profile_partial_preferences.groupby(level=0):
        if not ((profile_vs_profile_partial_preferences.droplevel(
                0).index == profiles_index).all() and
                (
                        profile_vs_profile_partial_preferences.columns ==
                        profiles_index).all()):
            raise ValueError(
                "DMs profile vs profile partial preferences should be passed "
                "as a DataFrame with "
                "identical index and columns")

    if not dms_profile_vs_profile_partial_preferences.dtypes.values.all() in [
        'float64', 'int64']:
        raise ValueError(
            "DMs profile vs profile partial preferences should be passed"
            " as a DataFrame with numeric values")


def _check_criteria_weights(weights: pd.Series):
    if not isinstance(weights, pd.Series):
        raise ValueError(
            "Criteria weights should be passed as a Series object")

    if weights.dtype not in ['float64', 'int64']:
        raise ValueError(
            "Criteria weights should be passed as a Series object "
            "with numeric values")

    if (weights <= 0).any():
        raise ValueError("Weights should be positive")


def _check_number_of_dms_gdss(
        dms_profiles_partial_preferences: List[pd.DataFrame],
        dms_alternatives_partial_preferences: List[pd.DataFrame],
        dms_profile_vs_profile_partial_preferences: pd.DataFrame):
    if not (len(dms_profiles_partial_preferences[0].index.get_level_values(
            0).unique()) ==
            len(dms_alternatives_partial_preferences[
                    0].index.get_level_values(0).unique()) ==
            len(dms_profile_vs_profile_partial_preferences.
                index.get_level_values(0).unique())):
        raise ValueError(
            "Number of DMs should be the same in every DMs"
            " partial preferences")


def _check_criteria_weights_gdss(
        dms_profiles_partial_preferences: List[pd.DataFrame],  # P(r,a)
        dms_alternatives_partial_preferences: List[pd.DataFrame],  # P(a,r)
        dms_profile_vs_profile_partial_preferences: pd.DataFrame,
        # P(r_i,r_j)
        criteria_weights: pd.Series):
    if not len(dms_profiles_partial_preferences[0].index.get_level_values(
            0).unique()) == \
           len(dms_alternatives_partial_preferences[0].index.get_level_values(
               0).unique()) == \
           len(dms_profile_vs_profile_partial_preferences.index.
               get_level_values(0).unique()) == len(criteria_weights):
        raise ValueError(
            "Number of criteria should be the same in every DMs partial "
            "preferences and criteria weights")


# M21x
def multiple_dm_criteria_net_flows_validation(
        dms_profiles_partial_preferences: List[pd.DataFrame],  # P(r,a)
        dms_alternatives_partial_preferences: List[pd.DataFrame],  # P(a,r)
        dms_profile_vs_profile_partial_preferences: pd.DataFrame,
        # P(r_i,r_j)
        criteria_weights: pd.Series):
    _check_dms_profiles_partial_preferences(dms_profiles_partial_preferences)
    _check_dms_alternatives_partial_preferences(
        dms_alternatives_partial_preferences)
    _check_dms_profile_vs_profile_partial_preferences(
        dms_profile_vs_profile_partial_preferences)
    _check_criteria_weights(criteria_weights)

    _check_number_of_dms_gdss(dms_profiles_partial_preferences,
                              dms_alternatives_partial_preferences,
                              dms_profile_vs_profile_partial_preferences)
    _check_criteria_weights_gdss(dms_profiles_partial_preferences,
                                 dms_alternatives_partial_preferences,
                                 dms_profile_vs_profile_partial_preferences,
                                 criteria_weights)
