from enum import Enum, auto


class SurrogateMethod(Enum):
    """Enumeration of surrogate weights methods."""

    EW = auto()
    RS = auto()
    RR = auto()
    ROC = auto()


class ScoringFunction(Enum):
    """
    Enumeration of the scoring functions.

    MAX: represent a max function
    MIN: represent a min function
    SUM: represent a sum function
    """

    MAX = auto()
    MIN = auto()
    SUM = auto()


class ScoringFunctionDirection(Enum):
    """
    Enumeration of the scoring function directions.

    IN_FAVOR: ScoringFunction(R(a,b))
    AGAINST: -ScoringFunction(R(b,a))
    DIFFERENCE: ScoringFunction(R(a,b) - R(b,a))
    """

    IN_FAVOR = auto()
    AGAINST = auto()
    DIFFERENCE = auto()


class CompareProfiles(Enum):
    """
    Enumeration of the compare profiles types.

    CENTRAL_PROFILES: represents a central profiles type
    BOUNDARY_PROFILES: represents a boundary profiles type
    LIMITING_PROFILES: represents a limiting profiles type
    """

    CENTRAL_PROFILES = auto()
    BOUNDARY_PROFILES = auto()
    LIMITING_PROFILES = auto()


class GeneralCriterion(Enum):
    """Enumeration of the preference functions."""

    USUAL = auto()
    U_SHAPE = auto()
    V_SHAPE = auto()
    LEVEL = auto()
    V_SHAPE_INDIFFERENCE = auto()
    GAUSSIAN = auto()


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

    BASIC = auto()
    PROFILE_BASED = auto()


class RelationType(Enum):
    """Enumeration of MCDA relation types."""

    PREFERENCE = auto()
    INDIFFERENCE = auto()
    INCOMPARABLE = auto()
    WEAK_PREFERENCE = auto()

    @classmethod
    def has_value(cls, x: "RelationType") -> bool:
        """Check if value is in enumeration.

        :param x:
        :return:
        """
        return x in cls

    @classmethod
    def content_message(cls) -> str:
        """Return list of items and their values.

        :return:
        """
        s = ", ".join(f"{item}: {item.value}" for item in cls)
        return "RelationType only has following values " + s
