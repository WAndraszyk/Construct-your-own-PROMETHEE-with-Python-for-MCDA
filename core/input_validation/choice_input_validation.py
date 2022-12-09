import pandas as pd
from typing import List

from core.constraint import Constraint, Relation

__all__ = ["decision_validation"]


def _check_flows(flows: pd.Series):
    if not isinstance(flows, pd.Series):
        raise TypeError("Flows should be passed as a DataSeries")
    for flow in flows:
        if not isinstance(flow, (int, float)):
            raise TypeError("Each flow should be a numeric value")


def _check_constraint(constraint: Constraint):
    if not isinstance(constraint.A, list):
        raise TypeError("Multipliers should be passed as a list of "
                        "numeric values")
    else:
        for i in constraint.A:
            if not isinstance(i, (int, float)):
                raise TypeError("Multipliers should be passed as a list of "
                                "numeric values")

    if constraint.relation not in [Relation.EQ, Relation.LEQ, Relation.GEQ]:
        raise TypeError("Relation should be passed as a Relation Enum")

    if not isinstance(constraint.b, (int, float)):
        raise TypeError("Right side of the condition should be passed as a "
                        "numeric value")


def _check_constraints(constraints: List[Constraint]):
    if not isinstance(constraints, list):
        raise TypeError("Constraints should be passed as a list of "
                        "Constraint objects")
    else:
        for constraint in constraints:
            if not isinstance(constraint, Constraint):
                raise TypeError("Constraints should be passed as a list of "
                                "Constraint objects")
            else:
                _check_constraint(constraint)


def decision_validation(flows: pd.Series, constraints: List[Constraint]):
    _check_flows(flows)
    _check_constraints(constraints)
