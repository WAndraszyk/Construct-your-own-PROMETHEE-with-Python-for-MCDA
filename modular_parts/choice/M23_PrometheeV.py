from core.aliases import NetOutrankingFlows
from core.constraint import Constraint
from core.linear_solver import solve_linear_problem
from typing import List
import pandas as pd

__all__ = ["compute_decision"]


def compute_decision(flows: NetOutrankingFlows, constraints: List[Constraint]) -> pd.Series:
    """
    Computes decision by solving a linear problem.

    :returns: alternatives that are part of the decision
    """
    alternatives = flows.index
    flows = flows.values
    constraints = constraints

    decision_tuple = solve_linear_problem(constraints, flows, len(flows))
    chosen_alternatives = []
    for i in range(len(decision_tuple)):
        if decision_tuple[i] == 1:
            chosen_alternatives.append(alternatives[i])

    return pd.Series(data=chosen_alternatives, name='chosen alternatives')
