# GENERALIZED_CRITERIA:
def usualCriterion(d: NumericValue):
    """
    Returns 0 if difference is less or equal to 0, if not it returns 1.

    :param d: difference between two alternatives on a specified criterion
    """
    return 1 if d > 0 else 0


def uShapeCriterion(d: NumericValue, q: NumericValue):
    """
    Returns 0 if difference is less or equal to q, if not it returns 1.

    :param d: difference between two alternatives on a specified criterion
    :param q: threshold of indifference
    """
    if d <= q:
        return 0
    else:
        return 1


def vShapeCriterion(d: NumericValue, p: NumericValue):
    """
    Returns 0 if difference is less or equal to p, 1 if it is greater then p.
    Else it calculates the number between 0 and 1 based on the difference.

    :param d: difference between two alternatives on a specified criterion
    :param p: threshold of strict prefference
    """
    if d <= 0:
        return 0
    elif d <= p:
        return round(d / p, self.decimal_place)
    else:
        return 1


def levelCriterion(d: NumericValue, p: NumericValue, q: NumericValue):
    """
    Returns: 0 for d<=q
             0.5 for q<d<=p
             1 for d>p

    :param d: difference between two alternatives on a specified criterion
    :param p: threshold of strict prefference
    :param q: threshold of indifference
    """
    if d <= q:
        return 0
    elif d <= p:
        return 0.5
    else:
        return 1


def vShapeIndifferenceCriterion(d: NumericValue, p: NumericValue, q: NumericValue):
    """
    Returns 0 if difference is less or equal to q, 1 if it is greater then p.
    Else it calculates the number between 0 and 1 based on the difference.

    :param d: difference between two alternatives on a specified criterion
    :param p: threshold of strict prefference
    :param q: threshold of indifference
    """
    if d <= q:
        return 0
    elif d <= p:
        return round((d - q) / (p - q), self.decimal_place)
    else:
        return 1


def gaussianCriterion(d: NumericValue, s: NumericValue):
    """
    Calculates preference based on nonlinear gaussian function.

    :param s: intermediate value between q and p. Defines the inflection point of the preference function.
    :param d: difference between two alternatives on a specified criterion
    """
    e = 2.718281828459045
    if d <= 0:
        return 0
    else:
        return 1 - e ** (-((d ** 2) / (2 * s ** 2)))