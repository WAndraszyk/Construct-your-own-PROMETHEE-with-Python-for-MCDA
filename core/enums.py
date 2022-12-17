from enum import Enum


class SurrogateMethod(Enum):
    """Enumeration of surrogate weights methods."""

    EW = 1
    RS = 2
    RR = 3
    ROC = 4


class ScoringFunction(Enum):
    """
    Enumeration of the scoring functions.

    MAX: represent a max function
    MIN: represent a min function
    SUM: represent a sum function
    """

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


class CompareProfiles(Enum):
    """
    Enumeration of the compare profiles types.

    CENTRAL_PROFILES: represents a central profiles type
    BOUNDARY_PROFILES: represents a boundary profiles type
    LIMITING_PROFILES: represents a limiting profiles type
    """

    CENTRAL_PROFILES = 1
    BOUNDARY_PROFILES = 2
    LIMITING_PROFILES = 3


class GeneralCriterion(Enum):
    """Enumeration of the preference functions."""

    USUAL = 1
    U_SHAPE = 2
    V_SHAPE = 3
    LEVEL = 4
    V_SHAPE_INDIFFERENCE = 5
    GAUSSIAN = 6


class InteractionType(Enum):
    """
    Enumeration of interaction type.

    STN: represents a strengthening interaction,
    WKN: represents a weakening interaction,
    ANT: represents an antagonistic interaction.
    """
    STN = 2
    WKN = 1
    ANT = -1


class Direction(Enum):
    """
    Enumeration of criteria direction.

    MAX: represents a maximized criterion
    MIN: represents a minimized criterion
    """

    MAX = 1
    MIN = 0


class FlowType(Enum):
    """
    Enumeration of flows type used to calculation.

    BASIC = represent flows of Promethee I (positive and negative flows)
    PROFILE_BASED = represent Promethee I flows, where the procedure for
    calculating flows for an alternative is to add the alternative to a
    group of profiles and calculate preferences in that group and use those
    preferences to calculate positive and negative flows
    """

    BASIC = 1
    PROFILE_BASED = 2
