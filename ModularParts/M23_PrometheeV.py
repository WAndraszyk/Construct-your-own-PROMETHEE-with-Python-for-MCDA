from typing import List
from core.aliases import NumericValue
from core.constraint import Constraint
from core.linear_solver import solve_linear_problem


class PrometheeV:
    def __init__(self, flows: List[NumericValue], constraints: List[Constraint]):
        self.flows = flows
        self.constraints = constraints

    def compute_decision(self):
        """
        Computes decision by solving a linear problem.

        :returns: decision tuple - 1 at position i means that alternative i is part of the decision
        """
        return solve_linear_problem(self.constraints, self.flows, len(self.flows))
