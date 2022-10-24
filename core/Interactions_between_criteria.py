from enum import Enum
from typing import List
from core.aliases import NumericValue


class InteractionType(Enum):
    # STN = 1  # strengthening
    # WKN = 2  # weakening
    # ANT = 3  # antagonistic
    STN = 1  # strengthening
    WKN = 1  # weakening
    ANT = -1  # antagonistic


class Interactions:
    def __init__(self, Criterion_A: List[str], Criterion_B: List[str],
                 Types: list[InteractionType], Coefficient: List[NumericValue]
                 ):
        """
        :param Criterion_A: List of criterion indexes
        :param Criterion_B: List of criterion indexes
        :param Types: List of interaction types. Interaction can be: strengthening, weakening or antagonistic.
        :param Coefficient: List of weights of the interaction coefficients

        """
        self.Criterion_A = Criterion_A
        self.Criterion_B = Criterion_B
        self.Types = Types
        self.Coefficient = Coefficient
