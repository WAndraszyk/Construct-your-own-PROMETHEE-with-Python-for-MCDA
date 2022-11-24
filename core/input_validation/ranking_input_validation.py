from enum import Enum

import pandas as pd

__all__ = ["promethee_i_ranking_validation", "_check_flows"]

# M11
from core.input_validation.flow_input_validation import net_flow_score_validation, _check_flows

def _check_weak_preference(weak_pref: bool):
    if not isinstance(weak_pref, bool):
        raise ValueError("Weak preference parameter should have value True or False")


def promethee_i_ranking_validation(flows: pd.DataFrame, weak_preference: bool):
    _check_flows(flows)
    _check_weak_preference(weak_preference)


def net_flow_score_iterative_validation(alternative_preferences: pd.DataFrame, function: Enum,
                                        direction: Enum, avoid_same_scores: bool):
    net_flow_score_validation(alternative_preferences, function, direction, avoid_same_scores)
