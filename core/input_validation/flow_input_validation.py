import pandas as pd

from typing import Tuple, Union, List

from core.enums import ScoringFunction, ScoringFunctionDirection, FlowType

__all__ = ["net_flow_score_validation", "promethee_group_ranking_validation",
           "basic_outranking_flows_validation",
           "profile_based_outranking_flows_validation",
           "calculate_net_outranking_flows_validation",
           "check_outranking_flows_type",
           "net_flows_for_multiple_DM_validation"]


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


def _check_scoring_function(function: ScoringFunction,
                            direction: ScoringFunctionDirection):
    """
    Check if scoring function and direction are valid.

    :param function: ScoringFunction enum
    :param direction: ScoringFunctionDirection enum
    :raises ValueError: if any of the parameters is not valid
    """

    # Check if scoring function is valid
    if not isinstance(function, ScoringFunction):
        raise ValueError(f"Incorrect scoring function: {function}")

    # Check if scoring function direction is valid
    if not isinstance(direction, ScoringFunctionDirection):
        raise ValueError(f"Incorrect scoring function direction: {direction}")


def _check_avoid_same_scores(avoid_same_scores: bool):
    """
    Check if avoid_same_scores is valid.

    :param avoid_same_scores: bool
    :raises ValueError: if avoid_same_scores is not valid
    """

    # Check if avoid_same_scores type is bool
    if not isinstance(avoid_same_scores, bool):
        raise ValueError("Avoid same scores parameter should be a boolean "
                         "value")


def _check_preferences(preferences: Union[pd.DataFrame,
                                          Tuple[pd.DataFrame, pd.DataFrame]]):
    """
    Check if preferences are valid.

    :param preferences: pd.DataFrame with alternatives as index and
    alternatives as columns or tuple of two pd.DataFrame with alternatives
    as index and profiles as columns in first pd.DataFrame and profiles as
    index and alternatives as columns in second pd.DataFrame
    :raises ValueError: if any preference is not valid
    """
    if isinstance(preferences, Tuple):
        if len(preferences) != 2:
            raise ValueError("Tuple of preferences should have two elements")

        for preference_table in preferences:
            # Check if preferences are passed as a DataFrame
            if not isinstance(preference_table, pd.DataFrame):
                raise ValueError(
                    "Preferences should be passed as a DataFrame "
                    "object")

            # Check if preferences dataframe has only numeric values
            if not preference_table.dtypes.values.all() in ['int32',
                                                            'int64',
                                                            'float32',
                                                            'float64']:
                raise ValueError("Preferences should be a numeric values")

        # Check if preferences have proper indexes and columns
        if not (preferences[0].index.equals(preferences[1].columns) and
                preferences[0].columns.equals(preferences[1].index)):
            raise ValueError("Preferences should have opposite indexes"
                             " and columns ( index_1 = columns_2 and"
                             " columns_1 = index_2 )")
    else:
        # Check if preferences are passed as a DataFrame
        if not isinstance(preferences, pd.DataFrame):
            raise ValueError("Preferences should be passed as a DataFrame "
                             "object")

        # Check if preferences dataframe has only numeric values
        if not preferences.dtypes.values.all() in ['int32', 'int64',
                                                   'float32', 'float64']:
            raise ValueError("Preferences should be a numeric values")

        # Check if preferences dataframe has index equals to columns
        if not preferences.index.equals(preferences.columns):
            raise ValueError("Preferences should have alternatives as index "
                             "and columns")


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
                             "alternatives vs profiles must have opposite"
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


def _check_flows_for_aggregated_flows(flows: pd.DataFrame):
    # Check if preferences are passed as a DataFrame
    if not isinstance(flows, pd.DataFrame):
        raise ValueError("Preferences should be passed as a DataFrame "
                         "object")

    # Check if preferences dataframe has only numeric values
    if not flows.dtypes.values.all() in ['int32', 'int64',
                                         'float32', 'float64']:
        raise ValueError("Preferences should be a numeric values")


def _check_dms_weights(dms_weights: pd.Series, n_dms: int):
    """
    Check if DM's weights are valid.

    :param dms_weights: pd.Series with DM names as index and weights as values
    :param n_dms: number of DM's
    :raises ValueError: if weights are not valid
    """

    # Check if weights are a Series
    if not isinstance(dms_weights, pd.Series):
        raise ValueError("DM's weights should be passed as a"
                         " Series object")

    # Check if there are enough weights
    if len(dms_weights) != n_dms:
        raise ValueError("Number of DM's weights should be equals "
                         "to number of DM's")

    # Check if weights are numeric
    if dms_weights.dtype not in ['int32', 'int64', 'float32', 'float64']:
        raise ValueError("DM's weights should be a numeric values")

    # Check if all weights are positive
    if (dms_weights <= 0).any():
        raise ValueError("DM's weights should be positive")


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


def _check_criteria_weights_gdss(
        dms_profiles_partial_preferences: List[pd.DataFrame],  # P(r,a)
        dms_alternatives_partial_preferences: List[pd.DataFrame],  # P(a,r)
        dms_profile_vs_profile_partial_preferences: pd.DataFrame,
        # P(r_i,r_j)
        criteria_weights: pd.Series):
    """
    Check if criteria weights are valid in FlowSortGDSS method.

    :param dms_profiles_partial_preferences: List with pd.DataFrame with
    MultiIndex(criteria, profiles) and alternatives as
    columns
    :param dms_alternatives_partial_preferences: List with pd.DataFrame
    with MultiIndex(criteria, alternatives)
    and profiles as columns
    :param dms_profile_vs_profile_partial_preferences: pd.DataFrame with
    MultiIndex(criteria, DMs, profiles) and MultiIndex(DMs, profiles)
    as columns
    :param criteria_weights: pd.Series with criteria weights
    :raise ValueError: if criteria weights are not valid
    """

    # Check if number of criteria weights is the same in every input
    if not len(dms_profiles_partial_preferences[0].index.get_level_values(
            0).unique()) == \
            len(dms_alternatives_partial_preferences[
                    0].index.get_level_values(0).unique()) == \
            len(dms_profile_vs_profile_partial_preferences.index.
                        get_level_values(0).unique()) == \
            len(criteria_weights):
        raise ValueError(
            "Number of criteria should be the same in every DMs partial "
            "preferences and criteria weights")


def _check_dms_profile_vs_profile_partial_preferences(
        dms_profile_vs_profile_partial_preferences: pd.DataFrame):
    """
    Check if DMs profile vs profile partial preferences are valid in
    FlowSortGDSS method.

    :param dms_profile_vs_profile_partial_preferences: pd.DataFrame with
    MultiIndex(criteria, DMs, profiles) and MultiIndex(DMs, profiles)
    as columns
    :raise ValueError: if DMs profile vs profile partial preferences are not
    valid
    """

    # Check if DMs profile vs profile partial preferences is a DataFrame
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

    # Check if DMs profile vs profile partial preferences have the same
    # length for each DM
    if len(dms_profile_vs_profile_partial_preferences.columns) != \
            columns_size:
        raise ValueError(
            "DMs profile vs profile partial preferences should be passed "
            "as a DataFrame with "
            "number of columns equal to number of all profiles")

    profiles_index = dms_profile_vs_profile_partial_preferences. \
        index.droplevel(0).unique()

    # Check if DMs profile vs profile partial preferences have the same
    for index, profile_vs_profile_partial_preferences in \
            dms_profile_vs_profile_partial_preferences.groupby(level=0):
        if not ((profile_vs_profile_partial_preferences.droplevel(
                0).index == profiles_index).all() and
                (profile_vs_profile_partial_preferences.columns ==
                 profiles_index).all()):
            raise ValueError(
                "DMs profile vs profile partial preferences should be passed "
                "as a DataFrame with "
                "identical index and columns")

    # Check if DMs profile vs profile partial preferences have numeric values
    if not dms_profile_vs_profile_partial_preferences.dtypes.values.all() in \
            ['int32', 'int64', 'float32', 'float64']:
        raise ValueError(
            "DMs profile vs profile partial preferences should be passed"
            " as a DataFrame with numeric values")


def _check_number_of_dms_gdss(
        dms_profiles_partial_preferences: List[pd.DataFrame],
        dms_alternatives_partial_preferences: List[pd.DataFrame],
        dms_profile_vs_profile_partial_preferences: pd.DataFrame):
    """
    Check if number of DMs in GDSS is valid in FlowSortGDSS method.

    :param dms_profiles_partial_preferences: List with pd.DataFrame with
    MultiIndex(criteria, profiles) and alternatives as
    columns
    :param dms_alternatives_partial_preferences: List with pd.DataFrame
    with MultiIndex(criteria, alternatives)
    and profiles as columns
    :param dms_profile_vs_profile_partial_preferences: pd.DataFrame with
    MultiIndex(criteria, DMs, profiles) and MultiIndex(DMs, profiles)
    as columns
    :raise ValueError: if number of DMs in GDSS is not valid
    """

    # Check if number of DMs in GDSS is the same in every input
    if not (len(dms_profiles_partial_preferences[0].
                        index.get_level_values(0).unique()) ==
            len(dms_alternatives_partial_preferences[0].
                        index.get_level_values(0).unique()) ==
            len(dms_profile_vs_profile_partial_preferences.
                        index.get_level_values(0).unique())):
        raise ValueError(
            "Number of DMs should be the same in every DMs"
            " partial preferences")


def _check_dms_alternatives_partial_preferences(
        dms_alternatives_partial_preferences: List[pd.DataFrame]):
    """
    Check if DMs alternatives partial preferences are valid in FlowSortGDSS
    method.

    :param dms_alternatives_partial_preferences: List with pd.DataFrame
    with MultiIndex(criteria, alternatives) and profiles as columns
    :raise ValueError: if DMs alternatives partial preferences are not valid
    """

    # Check if DMs alternatives partial preferences are passed in a list
    if not isinstance(dms_alternatives_partial_preferences, list):
        raise ValueError(
            "DMS alternatives partial preferences should be passed "
            "as a list of DataFrames")

    # Check if DMs alternatives partial preferences are DataFrames
    if not all(isinstance(dms_alternatives_partial_preference, pd.DataFrame)
               for dms_alternatives_partial_preference in
               dms_alternatives_partial_preferences):
        raise ValueError(
            "DMS alternatives partial preferences should be passed "
            "as a list of DataFrames")

    # Check if alternatives partial preferences have the same
    # number of alternatives
    if not all(len(dms_alternatives_partial_preference) ==
               len(dms_alternatives_partial_preferences[0]) for
               dms_alternatives_partial_preference in
               dms_alternatives_partial_preferences):
        raise ValueError(
            "Number of alternatives in every DMs alternatives partial"
            " preferences should be the same")

    # Check if alternatives partial preferences have the same
    # number of criteria
    if not all(len(dms_alternatives_partial_preference.columns) ==
               len(dms_alternatives_partial_preferences[0].columns)
               for dms_alternatives_partial_preference in
               dms_alternatives_partial_preferences):
        raise ValueError(
            "Number of criteria in every DMS alternatives partial "
            "preferences should be the same")

    if not all(dms_alternatives_partial_preference.dtypes.values.all() in
               ['int32', 'int64', 'float32', 'float64']
               for dms_alternatives_partial_preference in
               dms_alternatives_partial_preferences):
        raise ValueError(
            "DMs alternatives partial preferences should be passed "
            "as a list of DataFrames with "
            "numeric values")


def _check_dms_profiles_partial_preferences(
        dms_profiles_partial_preferences: List[pd.DataFrame]):
    """
    Check if DMs profiles partial preferences are valid in FlowSortGDSS
    method.

    :param dms_profiles_partial_preferences: List with pd.DataFrame with
    MultiIndex(criteria, profiles) and alternatives as columns
    :raise ValueError: if DMs profiles partial preferences are not valid
    """

    # Check if DMs profiles partial preferences are passed in a list
    if not isinstance(dms_profiles_partial_preferences, list):
        raise ValueError(
            "DMs profiles partial preferences should be passed "
            "as a list of DataFrames")

    # Check if DMs profiles partial preferences are DataFrames
    if not all(isinstance(dms_profiles_partial_preference, pd.DataFrame)
               for dms_profiles_partial_preference in
               dms_profiles_partial_preferences):
        raise ValueError(
            "DMs profiles partial preferences should be passed "
            "as a list of DataFrames")

    # Check if profiles partial preferences have the
    # same number of profiles for each DM
    if not all(len(dms_profiles_partial_preference) ==
               len(dms_profiles_partial_preferences[0]) for
               dms_profiles_partial_preference in
               dms_profiles_partial_preferences):
        raise ValueError(
            "Number of profiles in every DMs profiles partial "
            "preferences should be the same")

    # Check if profiles partial preferences have the same
    # number of criteria for each DM
    if not all(len(dms_profiles_partial_preference.columns) ==
               len(dms_profiles_partial_preferences[0].columns)
               for dms_profiles_partial_preference in
               dms_profiles_partial_preferences):
        raise ValueError(
            "Number of criteria in every DMs profiles partial "
            "preferences should be the same")

    # Check if profiles partial preferences have numeric values
    if not all(
            dms_profiles_partial_preference.dtypes.values.all()
            in ['int32', 'int64', 'float32', 'float64']
            for dms_profiles_partial_preference in
            dms_profiles_partial_preferences):
        raise ValueError(
            "DMs profiles partial preferences should be passed as "
            "a list of DataFrames with "
            "numeric values")


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


def net_flow_score_validation(alternative_preferences: pd.DataFrame,
                              function: ScoringFunction,
                              direction: ScoringFunctionDirection,
                              avoid_same_scores: bool):
    """
    Check if parameters for net flow score are valid.

    :param alternative_preferences: pd.DataFrame with alternatives as index
    and alternatives as columns
    :param function: ScoringFunction enum
    :param direction: ScoringFunctionDirection enum
    :param avoid_same_scores: bool
    :raises ValueError: if any of the parameters is not valid
    """
    _check_preferences(alternative_preferences)
    _check_scoring_function(function, direction)
    _check_avoid_same_scores(avoid_same_scores)


def promethee_group_ranking_validation(dms_flows: pd.DataFrame,
                                       dms_weights: pd.Series):
    """
    Check if parameters for PROMETHEE aggregated flows are valid.

    :param dms_flows: pd.DataFrame with alternatives as index and
    DM's names as columns
    :param dms_weights: pd.Series with DM's names as index and
    weights as values
    :raises ValueError: if any of the parameters is not valid
    """
    dms_from_flows = dms_flows.columns.unique()
    dms_from_weights = dms_weights.index

    _check_flows_for_aggregated_flows(dms_flows)
    _check_dms_weights(dms_weights, len(dms_from_flows))
    _check_if_criteria_are_the_same(dms_from_flows, dms_from_weights)


def basic_outranking_flows_validation(
        preferences: Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]):
    """
    Check if parameters for basic(PROMETHEE I) outranking flows are valid.

    :param preferences: pd.DataFrame with alternatives as index and
    alternatives as columns or tuple of two pd.DataFrame with alternatives
    as index and profiles as columns in first pd.DataFrame and profiles as
    index and alternatives as columns in second pd.DataFrame
    :raises ValueError: if any of the parameters is not valid
    """
    _check_preferences(preferences)


def profile_based_outranking_flows_validation(
        preferences: Tuple[pd.DataFrame, pd.DataFrame],
        profiles_preferences: pd.DataFrame):
    """
    Check if parameters for profile-based outranking flows method are valid.

    :param preferences: tuple of two pd.DataFrame with alternatives
    as index and profiles as columns in first pd.DataFrame and profiles as
    index and alternatives as columns in second pd.DataFrame
    :param profiles_preferences: pd.DataFrame with profiles as index and
    profiles as columns
    :raises ValueError: if any of the parameters is not valid
    """
    if isinstance(preferences, tuple):
        _check_preferences(preferences)
    else:
        raise ValueError(
            "Preferences should be passed as a tuple of DataFrames")
    _check_preferences(profiles_preferences)


def calculate_net_outranking_flows_validation(flows: pd.DataFrame):
    """
    Check if parameters for calculating Net outranking flows are valid.

    :param flows: pd.DataFrame with alternatives as index and 'positive' and
    'negative' columns
    :raises ValueError: if any of the parameters is not valid
    """
    _check_flows(flows)


def check_outranking_flows_type(flow_type: FlowType):
    """
    Check if outranking FlowType enum is valid.

    :param flow_type: FlowType enum
    :raises ValueError: if FlowType enum is not valid
    """
    if flow_type not in [FlowType.BASIC, FlowType.PROFILE_BASED]:
        raise ValueError(
            "Flow type should be either BASIC or PROFILE_BASED")


def net_flows_for_multiple_DM_validation(
        dms_profiles_partial_preferences: List[pd.DataFrame],  # P(r,a)
        dms_alternatives_partial_preferences: List[pd.DataFrame],  # P(a,r)
        dms_profile_vs_profile_partial_preferences: pd.DataFrame,  # P(r,r)
        criteria_weights: pd.Series):
    """
    Check if input for Net Flows for Multiple Decision Makers is valid.

    :param dms_profiles_partial_preferences: List of pd.DataFrame with
    MultiIndex(criteria, profiles) and alternatives as columns
    :param dms_alternatives_partial_preferences: List of pd.DataFrame with
    MultiIndex(criteria, alternatives) and profiles as columns
    :param dms_profile_vs_profile_partial_preferences: pd.DataFrame with
    MultiIndex(criteria, DMs, profiles) and MultiIndex(DMs, profiles)
     as columns
    :param criteria_weights: pd.Series with criteria as index and
    criteria weights as values
    :raise ValueError: if any input is not valid
    """
    _check_dms_profiles_partial_preferences(dms_profiles_partial_preferences)
    _check_dms_alternatives_partial_preferences(
        dms_alternatives_partial_preferences)
    _check_dms_profile_vs_profile_partial_preferences(
        dms_profile_vs_profile_partial_preferences)
    _check_weights(criteria_weights)

    _check_number_of_dms_gdss(dms_profiles_partial_preferences,
                              dms_alternatives_partial_preferences,
                              dms_profile_vs_profile_partial_preferences)
    _check_criteria_weights_gdss(dms_profiles_partial_preferences,
                                 dms_alternatives_partial_preferences,
                                 dms_profile_vs_profile_partial_preferences,
                                 criteria_weights)
