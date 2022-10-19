from core.aliases import NetOutrankingFlows
from core.constraint import Constraint
from core.linear_solver import solve_linear_problem
from typing import List
import pandas as pd


class PrometheeV:
    def __init__(self, flows: NetOutrankingFlows, constraints: List[Constraint]):
        self.alternatives = flows.index
        self.flows = flows.values
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

        return pd.Series(data=chosen_alternatives, name='chosen alternatives')
