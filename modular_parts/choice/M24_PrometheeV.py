"""
This module implements Promethee V method, which
maximises the result of {0,1} linear programming problem
by choosing appropriate set of alternatives.
"""
from core.constraint import Constraint
from core.linear_solver import solve_linear_problem
from core.input_validation import decision_validation
from typing import List
import pandas as pd

__all__ = ["compute_decision"]


def compute_decision(flows: pd.Series, constraints: List[Constraint]
                     ) -> pd.Series:
    """
    Computes decision by solving a linear problem.

    :param flows: Series of net flows with alternatives as index
    :param constraints: list of problem constraints

    :returns: Series of alternatives which are part of the decision
    """
    # input data validation
    decision_validation(flows, constraints)

    alternatives = flows.index
    flows = flows.values
    constraints = constraints

    # solve linear problem
    decision_tuple = solve_linear_problem(constraints, flows, len(flows))

    # find alternatives that create the solution
    chosen_alternatives = []
    for i in range(len(decision_tuple)):
        if decision_tuple[i] == 1:
            chosen_alternatives.append(alternatives[i])

    return pd.Series(data=chosen_alternatives, name='chosen alternatives')
