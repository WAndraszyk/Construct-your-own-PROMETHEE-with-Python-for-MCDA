from typing import Union, Tuple

from core.aliases import NumericValue
from core.enums import ScoringFunction, ScoringFunctionDirection
import pandas as pd

__all__ = ["promethee_i_ranking_validation",
           "promethee_iii_ranking_validation",

           "net_flow_score_iterative_validation",
           "promethee_ii_ranking_validation"]


from core.input_validation.flow_input_validation import \
    net_flow_score_validation


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


def _check_decimal_place(decimal_place: int):
    """
    Check if decimal place is valid.

    :param decimal_place: integer with decimal place
    :raises ValueError: if decimal place is not valid
    """

    # Check if decimal place is an integer
    if not isinstance(decimal_place, int):
        raise TypeError("Decimal place must be integer")

    # Check if decimal place is not negative
    if decimal_place < 0:
        raise ValueError("Decimal place must be not negative")


def _check_weak_preference(weak_preference: bool):
    """
    Check if weak preference is valid.

    :param weak_preference: boolean which indicates if weak preference is used
    :raises ValueError: if weak preference is not valid
    """

    # Check if weak preference is a boolean
    if not isinstance(weak_preference, bool):
        raise ValueError("Weak preference parameter should"
                         " be a boolean value")


def _check_net_flowsII(net_flows: pd.DataFrame):
    """
    Check if net flows II are valid.

    :param net_flows: pd.DataFrame with alternatives as index and
    'net' column at least
    :raise ValueError: if any net flow is not valid
    """

    # Check if net flows are passed as a DataFrame
    if not isinstance(net_flows, pd.DataFrame):
        raise TypeError(f"Net Flows should be passed as a DataFrame object")

    # Check if net flows dataframe have 'net' column
    if 'net' not in net_flows.columns:
        raise ValueError(f'No "net" column in given flows')

    # Check if net columns has numeric values
    if net_flows['net'].dtype not in ['int32', 'int64', 'float32', 'float64']:
        raise ValueError(f"Net Flow should be passed with numeric values")


def _check_alpha(alpha: NumericValue):
    if not isinstance(alpha, (int, float)):
        raise TypeError("Alpha must be a numeric value")
    if alpha <= 0:
        raise ValueError("Alpha must be greater than 0")


def promethee_ii_ranking_validation(net_flow: pd.DataFrame):
    """
    Check if all inputs are valid for Promethee II ranking.

    :param net_flow: pd.DataFrame with alternatives as index and
    'net' column at least
    :raise ValueError: if any input is not valid
    """
    _check_net_flowsII(net_flow)


def net_flow_score_iterative_validation(alternative_preferences: pd.DataFrame,
                                        function: ScoringFunction,
                                        direction: ScoringFunctionDirection):
    """
    Check if all inputs are valid for Net Flow Score Iterative.

    :param alternative_preferences: pd.DataFrame with alternatives as index
    and alternatives as columns
    :param function: ScoringFunction object
    :param direction: ScoringFunctionDirection object
    :raise ValueError: if any input is not valid
    """
    net_flow_score_validation(alternative_preferences, function, direction,
                              True)


def promethee_i_ranking_validation(flows: pd.DataFrame,
                                   weak_preference: bool):
    """
    Check if all inputs are valid for Promethee I ranking.

    :param flows: pd.DataFrame with alternatives as index and
    'positive', 'negative' columns
    :param weak_preference: boolean which indicates if weak preference is used
    :raise ValueError: if any input is not valid
    """
    _check_flows(flows)
    _check_weak_preference(weak_preference)


def promethee_iii_ranking_validation(flows: pd.DataFrame,
                                     preferences: pd.DataFrame,
                                     alpha: NumericValue,
                                     decimal_place: NumericValue):
    """
    Check if all inputs are valid for PrometheeIII ranking.

    :param flows: pd.DataFrame with alternatives as index and
    'positive', 'negative' columns
    :param preferences: pd.DataFrame with alternatives as index and
    alternatives as columns
    :param alpha: numeric value used to calculate intervals
    :param decimal_place: integer with decimal place
    :raise ValueError: if any input is not valid
    """
    _check_flows(flows)
    _check_preferences(preferences)
    _check_alpha(alpha)
    _check_decimal_place(decimal_place)
