import itertools
from typing import List, Tuple, Union

import numpy as np

from .constraint import Constraint, Relation


def solve_linear_problem(
    constraints: List[Constraint], C: List[Union[int, float]], n: int
) -> Tuple[int, ...]:
    """
    Solves given linear problem. Component value can be either 1 or 0.

    :param constraints: list of problem constraints
    :param C: list of coefficients in the goal function
    :param n: number of components
    :return: tuple of boolean values of components in the goal function
    """
    # generate possible solutions
    combinations = list(itertools.product([0, 1], repeat=n))

    max_Z = 0
    decision: Tuple[int, ...] = ()
    for combination in combinations:
        # calculate value for a given solution
        Z = np.dot(C, combination)
        # check if new solution value is greater than current maximum value
        if Z >= max_Z:
            flag = True
            # check if solution meets the constraints
            for constraint in constraints:
                if not check_constraint(constraint, combination):
                    flag = False
                    break
            # if solution meets the constraints set the solution as current
            # decision and its value as maximum value
            if flag:
                max_Z = Z
                decision = combination

    return decision


def check_constraint(constraint: Constraint, combination: Tuple[int, ...]) -> bool:
    """
    This function checks whether a given combination of values satisfies
    a given constraint.

    :param constraint: Constraint type, which represents a mathematical
                      constraint.
    :param combination: Tuple of integer values. It represents a
                        combination of values that needs to be checked against
                        the constraint.

    :return: The function returns a Boolean value indicating whether the
             given combination satisfies the given constraint.
    """
    if constraint.relation == Relation.EQ:
        return np.dot(combination, constraint.A) == constraint.b
    elif constraint.relation == Relation.GEQ:
        return np.dot(combination, constraint.A) >= constraint.b
    elif constraint.relation == Relation.LEQ:
        return np.dot(combination, constraint.A) <= constraint.b
    else:
        raise ValueError("Wrong relation operator")
