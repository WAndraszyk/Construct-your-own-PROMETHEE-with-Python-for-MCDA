import pandas as pd
from typing import Union, Tuple


def compute_single_criterion_net_flows(partial_preferences: Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]
                                       ) -> pd.DataFrame:
    """
    Compute the single criterion net flows for alternatives.

    :param partial_preferences: DataFrame with MultiIndex of criterion and alternative and alternative as columns.
    return: DataFrame with single criterion net flows
    """
    single_criterion_net_flows = pd.DataFrame(dtype=float)

    # for alternative vs profile and profile vs alternative cases
    if isinstance(partial_preferences, tuple):
        object_names = partial_preferences[1].columns.tolist()
        n = len(object_names)

        for (criterion, criterion_preferences1, criterion, criterion_preferences2) \
                in zip(partial_preferences[0].groupby(level=0),
                       partial_preferences[1].groupby(level=0)):
            for object_i, object_i_row, object_j, object_j_col \
                    in zip(criterion_preferences1.droplevel(0).iterrows(),
                           criterion_preferences2.droplevel(0).T.iterrows()):
                single_criterion_net_flows[object_i] = (object_i_row - object_j_col) / n

        single_criterion_net_flows = single_criterion_net_flows.T
        single_criterion_net_flows.columns = partial_preferences[0].index.get_level_values(0)
        single_criterion_net_flows.index = object_names
    else:
        object_names = partial_preferences.columns.tolist()
        n = len(object_names)

        for criterion, criterion_preferences in partial_preferences.groupby(level=0):
            for object_i, object_i_row, object_j, object_j_col \
                    in zip(criterion_preferences.droplevel(0).iterrows(),
                           criterion_preferences.droplevel(0).T.iterrows()):
                single_criterion_net_flows[object_i] = (object_i_row - object_j_col) / (n - 1)

        single_criterion_net_flows = single_criterion_net_flows.T
        single_criterion_net_flows.columns = partial_preferences.index.get_level_values(0)
        single_criterion_net_flows.index = object_names

    return single_criterion_net_flows
