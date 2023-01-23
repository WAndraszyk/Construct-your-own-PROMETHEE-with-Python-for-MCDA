from enum import Enum
from typing import List, Union


class Relation(Enum):
    """
    The Relation class represents a mathematical comparison operator,
    such as equality (=), greater than or equal (>=), or less than or
    equal(<=). It is an enumeration (Enum) with three possible values: EQ:
    represents the equality operator (=), GEQ: represents the greater than
    or equal operator (>=), LEQ: represents the less than or equal operator
    (<=).
    """

    EQ = 1
    GEQ = 2
    LEQ = 3


class Constraint:
    """
    The Constraint class represents a mathematical constraint of the form A
    relation b, where A is a list of multipliers, relation is a comparison
    operator (e.g. <, >=, etc.), and b is a constant value.
    """

    def __init__(
        self,
        A: List[Union[int, float]],
        relation: Relation,
        b: Union[int, float],
    ):
        """
        :param A: list of multipliers of left side of the condition
        :param relation: relation between left and right side of the condition
        :param b: value on the right side of the condition
        """
        self.A = A
        self.relation = relation
        self.b = b
