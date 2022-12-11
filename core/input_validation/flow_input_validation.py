import pandas as pd

from typing import Tuple, Union

from core.enums import ScoringFunction, ScoringFunctionDirection, FlowType

__all__ = ["net_flow_score_validation", "promethee_group_ranking_validation",
           "prometheeI_outranking_flows_validation",
           "prometheeII_outranking_flows_validation",
           "calculate_net_outranking_flows_validation",
           "check_outranking_flows_type"]


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


def _check_partial_preferences(partial_preferences: pd.DataFrame):
    # Check if partial preferences are passed as a DataFrame
    if not isinstance(partial_preferences, pd.DataFrame):
        raise ValueError("Partial preferences should be passed as a "
                         "DataFrame object")

    # Check if partial preferences dataframe has only numeric values
    if not partial_preferences.dtypes.values.all() in ['int32', 'int64',
                                                       'float32', 'float64']:
        raise ValueError("Partial preferences should be a numeric values")

    # Check if partial preferences dataframe has index equals to columns
    if partial_preferences.index.get_level_values(1).unique() != \
            partial_preferences.columns:
        raise ValueError("Partial preferences should have alternatives as "
                         "index and columns")

    # Check if partial preferences for each criterion has the same number of
    # alternatives
    n_alternatives = [len(criterion_preferences.index) for
                      _, criterion_preferences in
                      partial_preferences.groupby(level=0)]
    if not all(n == n_alternatives[0] for n in n_alternatives):
        raise ValueError("Partial preferences for each criterion should have "
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


def prometheeI_outranking_flows_validation(
        preferences: Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]):
    """
    Check if parameters for PROMETHEE I outranking flows are valid.

    :param preferences: pd.DataFrame with alternatives as index and
    alternatives as columns or tuple of two pd.DataFrame with alternatives
    as index and profiles as columns in first pd.DataFrame and profiles as
    index and alternatives as columns in second pd.DataFrame
    :raises ValueError: if any of the parameters is not valid
    """
    _check_preferences(preferences)


def prometheeII_outranking_flows_validation(
        preferences: Tuple[pd.DataFrame, pd.DataFrame],
        profiles_preferences: pd.DataFrame):
    """
    Check if parameters for PROMETHEE II outranking flows are valid.

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
    if flow_type not in [FlowType.PROMETHEE_I, FlowType.PROMETHEE_II]:
        raise ValueError(
            "Flow type should be either PROMETHEE_I or PROMETHEE_II")
