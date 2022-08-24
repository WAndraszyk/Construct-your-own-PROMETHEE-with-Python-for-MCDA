from enum import Enum
from typing import List
from core.aliases import NumericValue


class Relation(Enum):
    EQ = 1  # equals
    MT = 2  # more than
    LT = 3  # less than


class Constraint:
    def __init__(self, A: List[NumericValue], relation: Relation, b: NumericValue):
        """
        :param A: list of multipliers of left side of the condition
        :param relation: relation between left and right side of the condition
        :param b: value on the right side of the condition
        """
        self.A = A
        self.relation = relation
        self.b = b
