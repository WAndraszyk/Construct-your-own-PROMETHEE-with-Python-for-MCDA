from enum import Enum
from typing import List
from core.aliases import NumericValue


class Relation(Enum):
    """
        The Relation class represents a mathematical comparison operator,
        such as equality (=), greater than (>), or less than (<).
        It is an enumeration (Enum) with three possible values:
            EQ: represents the equality operator (=),
            MT: represents the greater than operator (>),
            LT: represents the less than operator (<).
    """
    EQ = 1
    MT = 2
    LT = 3


class Constraint:
    """
        The Constraint class represents a mathematical constraint of the form A relation b,
        where A is a list of multipliers, relation is a comparison operator (e.g. <, >=, etc.),
        and b is a constant value.
    """
    def __init__(self, A: List[NumericValue], relation: Relation, b: NumericValue):
        """
        :param A: list of multipliers of left side of the condition
        :param relation: relation between left and right side of the condition
        :param b: value on the right side of the condition
        """
        self.A = A
        self.relation = relation
        self.b = b
