from typing import List
from core.aliases import NumericValue
from core.constraint import Constraint
from core.linear_solver import solve_linear_problem


class PrometheeV:
    def __init__(self, alternatives: List[str], flows: List[NumericValue], constraints: List[Constraint]):
        self.alternatives = alternatives
        self.flows = flows
        self.constraints = constraints

    def compute_decision(self):
        """
        Computes decision by solving a linear problem.

        :returns: alternatives that are part of the decision
        """
        decision_tuple = solve_linear_problem(self.constraints, self.flows, len(self.flows))
        chosen_alternatives = []
        for i in range(len(decision_tuple)):
            if decision_tuple[i] == 1:
                chosen_alternatives.append(self.alternatives[i])
        return chosen_alternatives
