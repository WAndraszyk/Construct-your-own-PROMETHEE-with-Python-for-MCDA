import itertools
import numpy as np
from typing import List
from core.constraint import Constraint, Relation
from core.aliases import NumericValue


def check_constraint(constraint: Constraint, combination):
    if constraint.relation == Relation.EQ:
        return np.dot(combination, constraint.A) == constraint.b
    elif constraint.relation == Relation.MT:
        return np.dot(combination, constraint.A) >= constraint.b
    elif constraint.relation == Relation.LT:
        return np.dot(combination, constraint.A) <= constraint.b
    else:
        raise ValueError("Wrong relation operator")


def solve_linear_problem(constraints: List[Constraint], C: List[NumericValue], n: int):
    """
    Solves given linear problem. Component value can be either 1 or 0.

    :param constraints: list of problem constraints
    :param C: list of coefficients in the goal function
    :param n: number of components

    :returns: tuple of boolean values of components in the goal function
    """
    combinations = list(itertools.product([0, 1], repeat=n))

    max_Z = 0
    decision = ()
    for combination in combinations:
        Z = np.dot(C, combination)
        if Z >= max_Z:
            flag = True
            for constraint in constraints:
                if not check_constraint(constraint, combination):
                    flag = False
                    break
            if flag:
                max_Z = Z
                decision = combination

    return decision
