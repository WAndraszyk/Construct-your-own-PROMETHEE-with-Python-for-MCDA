import pandas as pd

__all__ = ["promethee_i_ranking_validation"]


def _check_flows(flows: pd.DataFrame):
    columns = flows.columns.values.tolist()

    if not isinstance(flows, pd.DataFrame):
        raise ValueError("Flows should be passed as a DataFrame object")

    if 'positive' not in columns or 'negative' not in columns:
        raise ValueError("Columns of DataFrame with flows should be named positive and negative")

    if len(columns) != 2:
        raise ValueError("DataFrame with flows should have two columns named positive and negative")

    for positive_flow, negative_flow in zip(flows['positive'], flows['negative']):
        if not isinstance(positive_flow, (int, float)) or not isinstance(negative_flow, (int, float)):
            raise ValueError("Flow should be a numeric values")


def _check_weak_preference(weak_pref: bool):
    if not isinstance(weak_pref, bool):
        raise ValueError("Weak preference parameter should have value True or False")


def promethee_i_ranking_validation(flows: pd.DataFrame, weak_preference: bool):
    _check_flows(flows)
    _check_weak_preference(weak_preference)
