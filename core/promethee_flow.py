from typing import Tuple, Union

import pandas as pd


def compute_single_criterion_net_flows(
    partial_preferences: Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]
) -> pd.DataFrame:
    """
    Compute the single criterion net flows for alternatives.
    The main idea of this function is to compute sum of subtractions of
    "alternatives vs alternatives" or "alternatives vs profiles" preferences.

    :param partial_preferences: pd.DataFrame with
        MultiIndex(criteria, alternatives) as index and
        alternatives as columns or Tuple of pd.DataFrame with
        MultiIndex(criteria, alternatives) as index and profiles as columns
        and pd.DataFrame with MultiIndex(criteria, profiles) as index and
        alternatives as columns. "alternatives" and "profiles" can be swapped
        for special cases.
    :return: pd.DataFrame with alternatives as index and criteria as columns.
    """

    # Init flows structure
    single_criterion_net_flows = pd.DataFrame(dtype=float)

    if isinstance(partial_preferences, tuple):
        # For "alternative vs profile" preferences

        # Save primal index of the passed objects
        object_names = partial_preferences[0].columns.tolist()
        n = len(object_names)

        # Iterate over criteria in both partial preferences DataFrames
        # simultaneously
        for (criterion, criterion_preferences1), (
            criterion,
            criterion_preferences2,
        ) in zip(
            partial_preferences[0].groupby(level=0),
            partial_preferences[1].groupby(level=0),
        ):
            # Transpose second DataFrame to get preferences where profiles
            # are preferred to alternative currently processed
            # in first DataFrame
            for (object_i, object_i_row), (object_j, object_j_col) in zip(
                criterion_preferences1.droplevel(0).iterrows(),
                criterion_preferences2.droplevel(0).T.iterrows(),
            ):
                single_criterion_net_flows.loc[object_i, criterion] = (
                    object_i_row - object_j_col
                ).sum() / n

    else:
        # For "alternative vs alternative" preferences

        # Save primal index of the passed DataFrame
        object_names = partial_preferences.columns.tolist()
        n = len(object_names)

        # Iterate over criteria in partial preferences DataFrame
        for criterion, criterion_preferences in partial_preferences.groupby(level=0):
            criterion_flows = []
            # Transpose second DataFrame to get preferences where alternatives
            # are preferred to alternative currently processed
            # in first iterated object
            for (object_i, object_i_row), (object_j, object_j_col) in zip(
                criterion_preferences.droplevel(0).iterrows(),
                criterion_preferences.droplevel(0).T.iterrows(),
            ):
                criterion_flows.append((object_i_row - object_j_col).sum() / (n - 1))
            single_criterion_net_flows[criterion] = criterion_flows

        # Set index of the returned DataFrame
        single_criterion_net_flows.index = object_names

    return single_criterion_net_flows
