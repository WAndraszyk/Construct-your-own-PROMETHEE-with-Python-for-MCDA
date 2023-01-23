from typing import List

import pandas as pd

from ..constraint import Constraint, Relation

__all__ = ["decision_validation"]


def _check_flows(flows: pd.Series):
    """
    Check if flows are valid.

    :param flows: pd.Series with alternatives as index and flows as values
    :raises ValueError: if flows are not valid
    """

    # Check if flows are a Series
    if not isinstance(flows, pd.Series):
        raise TypeError("Flows should be passed as a DataSeries")

    # Check if flows are numeric
    if flows.dtype not in ["int32", "int64", "float32", "float64"]:
        raise TypeError("Each flow should be a numeric value")


def _check_constraint(constraint: Constraint):
    """
    Check if constraint is valid.

    :param constraint: Constraint object
    :raises ValueError: if constraint is not valid
    """

    # Check if constraint multipliers list is a Constraint object
    if not isinstance(constraint.A, list):
        raise TypeError("Multipliers should be passed as a list of " "numeric values")

    # Check if all multipliers are numeric
    for i in constraint.A:
        if not isinstance(i, (int, float)):
            raise TypeError(
                "Multipliers should be passed as a list of " "numeric values"
            )

    # Check if constraint relation is a Constraint object
    if constraint.relation not in [Relation.EQ, Relation.LEQ, Relation.GEQ]:
        raise TypeError("Relation should be passed as a Relation Enum")

    # Check if constraint value is a Constraint object
    if not isinstance(constraint.b, (int, float)):
        raise TypeError(
            "Right side of the condition should be passed as a " "numeric value"
        )


def _check_constraints(constraints: List[Constraint]):
    """
    Check if all constraints are valid.

    :param constraints: list of Constraint objects
    :raises ValueError: if any of constraints is not valid
    """

    # Check if constraints is a list
    if not isinstance(constraints, list):
        raise TypeError(
            "Constraints should be passed as a list of " "Constraint objects"
        )

    # Check if all constraints are Constraint objects and
    # if all of them are valid
    for constraint in constraints:
        if not isinstance(constraint, Constraint):
            raise TypeError(
                "Constraints should be passed as a list of " "Constraint objects"
            )
        _check_constraint(constraint)


def decision_validation(flows: pd.Series, constraints: List[Constraint]):
    """
    Check if flows and constraints in PrometheeV are valid.

    :param flows: pd.Series with alternatives as index and flows as values
    :param constraints: list of Constraint objects
    :raises ValueError: if any flow or constraint is not valid
    """
    _check_flows(flows)
    _check_constraints(constraints)
