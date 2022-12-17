import pandas as pd

__all__ = ["alternatives_profiles_validation"]

from typing import Tuple, Union


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


def alternatives_profiles_validation(criteria_weights: pd.Series,
                                     partial_preferences: pd.DataFrame):
    """
    Check if input for PrometheeAlternativesProfiles is valid.

    :param criteria_weights: pd.Series with criteria as index and
    weights as values
    :param partial_preferences: pd.DataFrame with
    MultiIndex(criteria, alternatives) and columns as alternatives
    :raises ValueError: if input is not valid
    """
    criteria_from_df = partial_preferences.index.get_level_values(0).unique()
    criteria_from_series = criteria_weights.index

    _check_weights(criteria_weights)
    _check_partial_preferences(partial_preferences)
    _check_if_criteria_are_the_same(criteria_from_series, criteria_from_df)
