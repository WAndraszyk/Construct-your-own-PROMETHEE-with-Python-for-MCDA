import pandas as pd
from typing import List, Union, Tuple
from core.enums import CompareProfiles, Direction

__all__ = ["group_class_acceptabilities_validation", "prom_sort_validation",
           "promethee_tri_validation", "flow_sort_i_validation",
           "flow_sort_ii_validation", "flow_sort_gdss_validation"]


def _check_flows(flows: pd.DataFrame):
    """
    Check if flows are valid.

    :param flows: pd.DataFrame with alternatives as index and
    'positive', 'negative' columns
    :raises ValueError: if any flow is not valid
    """

    # Check if flows are passed as a DataFrame
    if not isinstance(flows, pd.DataFrame):
        raise ValueError("Flows should be passed as a DataFrame object")

    # Check if flows dataframe have 'positive' and 'negative' columns
    if 'positive' not in flows.columns or 'negative' not in flows.columns:
        raise ValueError("Flows dataframe should have 'positive' "
                         "and 'negative' flows")

    # Check if flows dataframe have only positive and negative flows
    if len(flows.columns) != 2:
        raise ValueError("DataFrame with flows should have only two columns "
                         "named positive and negative")

    # Check if flows are numeric values
    if not flows.dtypes.values.all() in ['int32', 'int64',
                                         'float32', 'float64']:
        raise ValueError("Flows should be a numeric values")


def _check_partial_preferences(
        partial_preferences: Union[pd.DataFrame,
                                   Tuple[pd.DataFrame, pd.DataFrame]],
        with_profiles: bool = False):
    """
    Check if partial preferences are valid.

    :param partial_preferences: pd.DataFrame with
    MultiIndex(criteria, alternatives) and alternatives as columns
    or Tuple of two pd.DataFrame with MultiIndex(criteria, alternatives)
    and profiles as columns in first pd.DataFrame and
    MultiIndex(criteria, profiles) and alternatives as columns
    in second pd.DataFrame
    :param with_profiles: if True partial preferences are
    alternative vs profiles (helps in handling tuple case)
    :raises TypeError: if partial preferences are not valid
    """
    if isinstance(partial_preferences, Tuple):
        for partial_preference in partial_preferences:
            _check_partial_preferences(partial_preference, True)

        if partial_preferences[0].index.equals(
                partial_preferences[1].columns) or \
                partial_preferences[1].index.equals(
                    partial_preferences[0].columns):
            raise ValueError("Partial preferences for "
                             "alternatives vs profiles must have oposite"
                             " indexes and columns")
    else:
        # Check if partial preferences are passed as a DataFrame
        if not isinstance(partial_preferences, pd.DataFrame):
            raise ValueError("Partial preferences should be passed as a "
                             "DataFrame object")

        # Check if partial preferences dataframe has only numeric values
        if not partial_preferences.dtypes.values.all() in ['int32',
                                                           'int64',
                                                           'float32',
                                                           'float64']:
            raise ValueError("Partial preferences should be a numeric values")

        # Check if partial preferences dataframe has index equals to columns
        if not partial_preferences.index.get_level_values(1).unique().equals(
                partial_preferences.columns) and not with_profiles:
            raise ValueError(
                "Partial preferences should have alternatives/profiles as "
                "index and columns")

        # Check if partial preferences for each criterion has the same
        # number of alternatives
        n_alternatives = [len(criterion_preferences.index) for
                          _, criterion_preferences in
                          partial_preferences.groupby(level=0)]
        if not all(n == n_alternatives[0] for n in n_alternatives):
            raise ValueError(
                "Partial preferences for each criterion should have "
                "the same number of alternatives")


def _check_weights(weights: pd.Series):
    """
    Check if weights are valid.

    :param weights: pd.Series with criteria as index and weights as values
    :raises ValueError: if weights are not valid
    """

    # Check if weights are a Series
    if not isinstance(weights, pd.Series):
        raise ValueError("Criteria weights should be passed as a"
                         " Series object")

    # Check if weights are numeric
    if weights.dtype not in ['int32', 'int64', 'float32', 'float64']:
        raise ValueError("Weights should be a numeric values")

    # Check if all weights are positive
    if (weights <= 0).any():
        raise ValueError("Weights should be positive")


def _check_categories(categories: List[str]):
    """
    Check if categories are valid.

    :param categories: List of categories names as strings
    :raises ValueError: if categories are not valid
    """

    # Check if categories are passed in a List
    if not isinstance(categories, List):
        raise ValueError("Categories should be passed as a "
                         "List of string objects")

    # Check if categories are strings
    for category in categories:
        if not isinstance(category, str):
            raise ValueError("Category should be a string")


def _check_assignments(assignments: List[pd.DataFrame],
                       categories: List[str]):
    """
    Check if assignments are valid.

    :param assignments: List of pd.DataFrame with alternatives as index
    and 'better', 'worse' columns (imprecise assignments)
    :param categories: List of categories names as strings
    :raises ValueError: if assignments are not valid
    """
    # Check if assignments are passed in a List
    if not isinstance(assignments, List):
        raise ValueError("Assignments should be passed as a "
                         "List of DataFrame objects")

    for assignment in assignments:
        # Check if assignments are passed as a DataFrame
        if not isinstance(assignment, pd.DataFrame):
            raise ValueError("Each assignment of DM should be "
                             "passed as a DataFrame object")

        # Check if assignments dataframe have 'better' and 'worse' columns
        if 'worse' not in assignment.columns or \
                'better' not in assignment.columns:
            raise ValueError("Columns of DataFrame with assignments"
                             " should be named worse and better")

        # Check if assignments dataframe have only valid categories
        for worse_cat, better_cat in zip(assignment['worse'],
                                         assignment['better']):
            if worse_cat not in categories or better_cat not in categories:
                raise ValueError("Alternative can not be assign to category"
                                 " that does not exist in categories list")


def _check_if_criteria_are_the_same(criteria_1: pd.Index,
                                    criteria_2: pd.Index):
    """
    Check if two criteria are the same.

    :param criteria_1: pd.Index with criteria names
    :param criteria_2: pd.Index with criteria names
    :raises ValueError: if criteria are not the same
    """

    # Check if criteria are the same
    if not criteria_1.equals(criteria_2):
        raise ValueError("Criteria are not the same in different objects")


def _check_preference_thresholds(preference_thresholds: pd.Series,
                                 criteria: pd.Index):
    """
    Check if preference thresholds are valid.

    :param preference_thresholds: pd.Series with criteria as index and
    preference thresholds as values
    :param criteria: pd.Index with criteria names
    :raise ValueError: if preference thresholds are not valid
    """

    # Check if preference thresholds are a Series
    if not isinstance(preference_thresholds, pd.Series):
        raise TypeError("Preference thresholds should be passed as "
                        "a Series object")

    _check_if_criteria_are_the_same(preference_thresholds.index, criteria)

    # Check if preference thresholds are numeric
    for threshold in preference_thresholds:
        if not (isinstance(threshold, int) or isinstance(threshold, float)
                or threshold is None):
            raise TypeError("Preference thresholds should be numeric values"
                            " or None")

    # Check if preference thresholds are not negative
    if (preference_thresholds < 0).any():
        raise ValueError("Preference thresholds can not be lower than 0")


def _check_performances(performances: pd.DataFrame):
    """
    Check if performances are valid.

    :param performances: pd.DataFrame with alternatives or profiles as index
    and criteria as columns
    :raise ValueError: if performances are not valid
    """

    # Check if performances are a DataFrame
    if not isinstance(performances, pd.DataFrame):
        raise ValueError("Performances should be passed "
                         "as a DataFrame")

    # Check if performances are numeric
    if not performances.dtypes.values.all() in ['int32', 'int64',
                                                'float32', 'float64']:
        raise ValueError("Performances should be passed "
                         "with int or float values")


def _check_criteria_directions(criteria_directions: pd.Series):
    """
    Check if criteria directions are valid.

    :param criteria_directions: pd.Series with criteria as index and
    Direction objects as values
    :raise ValueError: if any criteria direction is not valid
    """

    # Check if criteria directions are a Series
    if not isinstance(criteria_directions, pd.Series):
        raise ValueError("Criteria directions should be a Series object")

    # Check if criteria directions are Direction enums
    if criteria_directions.values.any() not in [Direction.MAX, Direction.MIN]:
        raise ValueError(
            "Criteria directions should be core.enums.Direction enums")


def _check_cut_point(cut_point: Union[int, float]):
    """
    Check if cut point is valid.

    :param cut_point: int or float
    :raise ValueError: if cut point is not valid
    """

    # Check if cut point is numeric
    if not isinstance(cut_point, (int, float)):
        raise ValueError("Cut point parameter should be passed a"
                         " numeric values")


def _check_assign_to_better(assign_to_better: bool):
    """
    Check if assign_to_better is valid.

    :param assign_to_better: bool
    :raise ValueError: if assign_to_better is not valid
    """

    # Check if assign_to_better is bool
    if not isinstance(assign_to_better, bool):
        raise ValueError("Assign to better class parameter should"
                         " have value True or False")


def _check_marginal_val(use_marginal_val: bool):
    """
    Check if use_marginal_val is valid.

    :param use_marginal_val: bool
    :raise ValueError: if use_marginal_val is not valid
    """

    # Check if use_marginal_val is bool
    if not isinstance(use_marginal_val, bool):
        raise ValueError("Use marginal value parameter should "
                         "have value True or False")


def _check_compare_profiles(compare_profiles: CompareProfiles):
    """
    Check if compare_profiles is valid.

    :param compare_profiles: CompareProfiles object
    :raise TypeError: if compare_profiles is not valid
    """

    # Check if compare_profiles is CompareProfiles object
    if not isinstance(compare_profiles, CompareProfiles):
        raise TypeError("Compare profiles parameter should be "
                        "core.enums.CompareProfiles enum")


def _check_compare_profiles_type_and_profiles_and_categories_length(
        compare_profiles: CompareProfiles,
        categories: List[str],
        category_profiles: pd.DataFrame,
        gdss: bool = False):
    """
    Check if compare_profiles is valid.

    :param compare_profiles: CompareProfiles object
    :param categories: List with categories names as strings
    :param category_profiles: pd.DataFrame with profiles as index and
    criteria as columns
    :param gdss: bool, True if used for FlowSortGDSS validation
    :raise ValueError: if compare_profiles is not valid
    """

    # Check if number of profiles is proper for passed
    # compare_profiles parameter
    if compare_profiles is CompareProfiles.LIMITING_PROFILES:
        # FlowSortGDSS can not use limiting profiles
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
    """
    Check if Promethee II flows are valid.

    :param prometheeII_flows: pd.DataFrame with alternatives/profiles
    as index and 'positive', 'negative' and 'net' columns
    :param category_profiles: pd.DataFrame with profiles as index and
    criteria as columns
    :raise ValueError: if Promethee II flows are not valid
    """

    # Check if Promethee II flows are a DataFrame
    if not isinstance(prometheeII_flows, pd.DataFrame):
        raise ValueError(
            "PrometheeII flows should be passed as a DataFrame object")

    # Check if Promethee II flows have MultiIndex
    if not isinstance(prometheeII_flows.index, pd.MultiIndex):
        raise ValueError(
            "PrometheeII flows should be passed as a DataFrame with "
            "MultiIndex")

    # Check if Promethee II flows have proper columns
    if prometheeII_flows.columns.tolist() != ['positive', 'negative', 'net']:
        raise ValueError(
            "PrometheeII flows should be passed as a DataFrame with "
            "columns: positive, negative, net")

    # Check if Promethee II flows 'groups' have equal length
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


def _check_net_flows(net_flows: pd.Series):
    """
    Check if net flows are valid.

    :param net_flows: pd.Series with alternatives/profiles as index
    and net flows as values
    :raise ValueError: if net flows are not valid
    """

    # Check if net flows are a Series
    if not isinstance(net_flows, pd.Series):
        raise ValueError("Net flows should be passed as a Series object")

    # Check if net flows have numeric values
    if net_flows.dtype not in ['int32', 'int64', 'float32', 'float64']:
        raise ValueError(
            "Net flows should be passed as a Series with numeric values")


def _check_profiles_general_net_flows(
        profiles_general_net_flows: pd.DataFrame,
        alternatives_general_net_flows: pd.Series,
        profiles_performances: List[pd.DataFrame]):
    """
    Check if profiles general net flows are valid.

    :param profiles_general_net_flows: pd.DataFrame with
    MultiIndex(DM's, profiles) and alternatives as columns
    :param alternatives_general_net_flows: pd.Series with alternatives
    as index and general net flows as values
    :param profiles_performances: List with pd.DataFrame with
    profiles as index and criteria as columns
    :raise ValueError: if profiles general net flows are not valid
    """

    # Check if profiles general net flows are a DataFrame
    if not isinstance(profiles_general_net_flows, pd.DataFrame):
        raise ValueError(
            "Profiles general net flows should be passed as a "
            "DataFrame object")

    # Check if profiles general net flows have MultiIndex
    if not isinstance(profiles_general_net_flows.index, pd.MultiIndex):
        raise ValueError(
            "Profiles general net flows should be passed as a DataFrame "
            "with MultiIndex")

    # Check if profiles general net flows have proper columns and indexes
    if not (profiles_general_net_flows.columns ==
            alternatives_general_net_flows.index).all():
        raise ValueError(
            "Profiles general net flows should have columns equals to "
            "alternatives general net flows index")

    # Check if profiles general net flows have the same
    # number of profiles for each DM
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

    # Check if profiles general net flows have numeric values
    if profiles_general_net_flows.dtypes.values.any() not in ['int32',
                                                              'int64',
                                                              'float32',
                                                              'float64']:
        raise ValueError(
            "Profiles general net flows should be passed as a DataFrame "
            "with numeric values")


def _check_profiles_performances_list(
        profiles_performances: List[pd.DataFrame]):
    """
    Check if profiles performances are valid.

    :param profiles_performances: List with pd.DataFrame with
    profiles as index and criteria as columns
    :raise ValueError: if profiles performances are not valid
    """

    # Check if profiles performances are passed in a list
    if not isinstance(profiles_performances, list):
        raise ValueError(
            "Profiles performances should be passed as a list of DataFrames")

    # Check if profiles performances are DataFrames
    if not all(isinstance(profiles_performance, pd.DataFrame) for
               profiles_performance in profiles_performances):
        raise ValueError(
            "Profiles performances should be passed as a list of DataFrames")

    # Check if profiles performances have the same number of profiles
    if not all(len(profiles_performance) ==
               len(profiles_performances[0]) for profiles_performance in
               profiles_performances):
        raise ValueError(
            "Number of profiles in every profiles performances "
            "should be the same")

    # Check if profiles performances have the same number of criteria
    if not all(len(profiles_performance.columns) == len(
            profiles_performances[0].columns)
               for profiles_performance in profiles_performances):
        raise ValueError(
            "Number of criteria in every profiles performances "
            "should be the same")

    # Check if profiles performances have numeric values
    if not all(
            profiles_performance.dtypes.values.all() in ['int32', 'int64',
                                                         'float32', 'float64']
            for profiles_performance in profiles_performances):
        raise ValueError(
            "Profiles performances should be passed as a list of "
            "DataFrames with numeric values")


def _check_dms_weights(dms_weights: pd.Series,
                       profiles_general_net_flows: pd.DataFrame):
    """
    Check if DMs weights are valid in FlowSortGDSS method.

    :param dms_weights: pd.Series with DMs as index and weights as values
    :param profiles_general_net_flows: pd.DataFrame with
    MultiIndex(DM's, profiles) and alternatives as columns
    :raise ValueError: if DMs weights are not valid
    """

    # Check if DMs weights are a Series
    if not isinstance(dms_weights, pd.Series):
        raise ValueError("DM's weights should be passed as a Series object")

    # Check if DMs weights are positive values
    if (dms_weights <= 0).any():
        raise ValueError("DMS weights should be positive")

    # Check if DMs weights have the same index as profiles general net flows
    if not (dms_weights.index ==
            profiles_general_net_flows.index.get_level_values(
                0).unique()).all():
        raise ValueError(
            "DMS weights should have index equals to profiles"
            " general net flows index")


def _check_number_of_dms(profiles_general_net_flows: pd.DataFrame,
                         profiles_performances: List[pd.DataFrame],
                         dms_weights: pd.Series):
    """
    Check if number of DMs is valid in FlowSortGDSS method.

    :param profiles_general_net_flows: pd.DataFrame with
    MultiIndex(DM's, profiles) and alternatives as columns
    :param profiles_performances: List with pd.DataFrame with
    profiles as index and criteria as columns
    :param dms_weights: pd.Series with DMs as index and weights as values
    :raise ValueError: if number of DMs is not valid
    """

    # Check if number of DMs are equal in every input of FlowSortGDSS method
    if not len(profiles_performances) == len(dms_weights.index) == \
           len(profiles_general_net_flows.index.get_level_values(0).unique()):
        raise ValueError(
            "Number of DMs in profiles performances should be"
            " the same as in DMS weights and "
            "in profiles general net flows")


def prom_sort_validation(categories: List[str],
                         alternatives_flows: pd.DataFrame,
                         category_profiles_flows: pd.DataFrame,
                         preference_thresholds: pd.Series,
                         category_profiles: pd.DataFrame,
                         criteria_directions: pd.Series,
                         cut_point: Union[int, float],
                         assign_to_better_class: bool = True):
    """
    Check if parameters for Prom Sort are valid.

    :param categories: List of categories names as strings
    :param alternatives_flows: pd.DataFrame with alternatives as index
    and 'positive' and 'negative' columns
    :param category_profiles_flows: pd.DataFrame with categories as index
    and 'positive' and 'negative' columns
    :param preference_thresholds: pd.Series with criteria as index and
    preference thresholds as values
    :param category_profiles: pd.DataFrame with profiles as index
    and criteria as columns
    :param criteria_directions: pd.Series with criteria as index and
    Direction objects as values
    :param cut_point: int or float, helps in ambiguous cases
    :param assign_to_better_class: bool, helps in ambiguous cases
    :raise ValueError: if any parameter is not valid
    """
    criteria_from_df = category_profiles.columns.unique()

    _check_categories(categories)
    _check_flows(alternatives_flows)
    _check_flows(category_profiles_flows)
    _check_preference_thresholds(preference_thresholds, criteria_from_df)
    _check_performances(category_profiles)
    _check_criteria_directions(criteria_directions)
    _check_cut_point(cut_point)
    _check_assign_to_better(assign_to_better_class)


def promethee_tri_validation(categories: List[str],
                             criteria_weights: pd.Series,
                             alternatives_partial_preferences: Tuple[
                                 pd.DataFrame, pd.DataFrame],
                             profiles_partial_preferences: pd.DataFrame,
                             assign_to_better_class: bool = True,
                             use_marginal_value: bool = True):
    """
    Check if input for PROMETHEE TRI method is valid.

    :param categories: List of categories names as strings
    :param criteria_weights: pd.Series with criteria as index and
    criteria weights as values
    :param alternatives_partial_preferences: Tuple of two pd.DataFrame with
    MultiIndex(criteria, alternatives) and profiles as columns in first
    pd.DataFrame and MultiIndex(criteria, profiles) and alternatives
    as columns in second pd.DataFrame
    :param profiles_partial_preferences: pd.DataFrame with MultiIndex(
    criteria, profiles) and profiles as columns
    :param assign_to_better_class: bool, helps in ambiguous cases
    :param use_marginal_value: bool, helps in ambiguous cases
    :raise ValueError: if any input is not valid
    """
    criteria_from_df = alternatives_partial_preferences[0].index. \
        get_level_values(0).unique()

    _check_categories(categories)
    _check_if_criteria_are_the_same(criteria_from_df, criteria_weights.index)
    _check_weights(criteria_weights)
    _check_partial_preferences(alternatives_partial_preferences)
    _check_partial_preferences(profiles_partial_preferences)
    _check_assign_to_better(assign_to_better_class)
    _check_marginal_val(use_marginal_value)


def flow_sort_i_validation(categories: List[str],
                           category_profiles: pd.DataFrame,
                           criteria_directions: pd.Series,
                           alternatives_flows: pd.DataFrame,
                           category_profiles_flows: pd.DataFrame,
                           comparison_with_profiles: CompareProfiles):
    """
    Check if input for FlowSortI is valid.

    :param categories: List of categories names as strings
    :param category_profiles: pd.DataFrame with profiles as index and
    criteria as columns
    :param criteria_directions: pd.Series with criteria as index and
    Direction objects as values
    :param alternatives_flows: pd.DataFrame with alternatives as index and
    'positive' and 'negative' columns
    :param category_profiles_flows: pd.DataFrame with profiles as index and
    'positive' and 'negative' columns
    :param comparison_with_profiles: CompareProfiles object, indicates
    type of profiles (limiting, boundary, central)
    :raise ValueError: if any input is not valid
    """
    criteria_from_df = category_profiles.columns.unique()

    _check_if_criteria_are_the_same(criteria_from_df,
                                    criteria_directions.index)
    _check_categories(categories)
    _check_performances(category_profiles)
    _check_criteria_directions(criteria_directions)
    _check_flows(alternatives_flows)
    _check_flows(category_profiles_flows)
    _check_compare_profiles(comparison_with_profiles)


def flow_sort_ii_validation(categories: List[str],
                            category_profiles: pd.DataFrame,
                            criteria_directions: pd.Series,
                            prometheeII_flows: pd.DataFrame,
                            comparison_with_profiles: CompareProfiles):
    """
    Check if inputs are valid in FlowSortII method.

    :param categories: List with categories names
    :param category_profiles: pd.DataFrame with categories as index and
    profiles as columns
    :param criteria_directions: pd.Series with criteria as index and
    directions as values
    :param prometheeII_flows: pd.DataFrame with MultiIndex(categories,
    profiles) and criteria as columns
    :param comparison_with_profiles: CompareProfiles object
    :raise ValueError: if inputs are not valid
    """
    _check_categories(categories)
    _check_performances(category_profiles)
    _check_criteria_directions(criteria_directions)
    _check_prometheeII_flows(prometheeII_flows, category_profiles)
    _check_compare_profiles_type_and_profiles_and_categories_length(
        comparison_with_profiles, categories,
        category_profiles)
    _check_if_criteria_are_the_same(category_profiles.columns,
                                    criteria_directions.index)


def flow_sort_gdss_validation(alternatives_general_net_flows: pd.Series,
                              profiles_general_net_flows: pd.DataFrame,
                              categories: List[str],
                              criteria_directions: pd.Series,
                              profiles_performances: List[pd.DataFrame],
                              dms_weights: pd.Series,
                              comparison_with_profiles: CompareProfiles,
                              assign_to_better_class: bool = True):
    """
    Check if inputs are valid in FlowSortGDSS method.

    :param alternatives_general_net_flows: pd.Series with alternatives as
    index and general net flows as values
    :param profiles_general_net_flows: pd.DataFrame with MultiIndex(DM's,
    profiles) and alternatives as columns
    :param categories: List with categories names
    :param criteria_directions: pd.Series with criteria as index and
    directions as values
    :param profiles_performances: List with pd.DataFrame with profiles as
    index and criteria as columns
    :param dms_weights: pd.Series with DMs as index and weights as values
    :param comparison_with_profiles: CompareProfiles object
    :param assign_to_better_class: bool, if True, assign alternatives to
    better class, if False, assign alternatives to worse class
    in ambiguous case
    :raise ValueError: if inputs are not valid
    """
    _check_net_flows(alternatives_general_net_flows)
    _check_profiles_general_net_flows(profiles_general_net_flows,
                                      alternatives_general_net_flows,
                                      profiles_performances)
    _check_categories(categories)
    _check_criteria_directions(criteria_directions)
    _check_profiles_performances_list(profiles_performances)
    _check_dms_weights(dms_weights, profiles_general_net_flows)
    _check_compare_profiles(comparison_with_profiles)
    _check_compare_profiles_type_and_profiles_and_categories_length(
        comparison_with_profiles, categories,
        profiles_performances[0], True)
    _check_assign_to_better(assign_to_better_class)


def group_class_acceptabilities_validation(categories: List[str],
                                           assignments: List[pd.DataFrame]):
    """
    Check if input is valid for Group Class Acceptabilities module.

    :param categories: List of categories names as strings
    :param assignments: List of pd.DataFrame with alternatives as index
    and 'better', 'worse' columns (imprecise assignments)
    :raises ValueError: if alternatives support is not valid
    """
    _check_categories(categories)
    _check_assignments(assignments, categories)
