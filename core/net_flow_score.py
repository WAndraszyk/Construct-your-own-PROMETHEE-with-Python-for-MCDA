from enum import Enum


class ScoringFunction(Enum):
    """Enumeration of the scoring functions."""

    MAX = 1
    MIN = 2
    SUM = 3


class ScoringFunctionDirection(Enum):
    """
    Enumeration of the scoring function directions.

    IN_FAVOR: ScoringFunction(R(a,b))
    AGAINST: -ScoringFunction(R(b,a))
    DIFFERENCE: ScoringFunction(R(a,b) - R(b,a))
    """

    IN_FAVOR = 1
    AGAINST = 2
    DIFFERENCE = 3