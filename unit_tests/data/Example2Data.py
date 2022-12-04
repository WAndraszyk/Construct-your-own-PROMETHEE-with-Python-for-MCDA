import pandas as pd

from core.preference_commons import GeneralCriterion
from core.enums import *

alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
criteria = ['g1', 'g2', 'g3', 'g4', 'g5', 'g6']
alternatives_performances = [
    [80, 90, 6, 5.4, 8, 5],
    [65, 58, 2, 9.7, 1, 1],
    [83, 60, 4, 7.2, 4, 7],
    [40, 80, 10, 7.5, 7, 10],
    [52, 72, 6, 2.0, 3, 8],
    [94, 96, 7, 3.6, 5, 6]
]

generalized_criterion = [GeneralCriterion.U_SHAPE, GeneralCriterion.V_SHAPE,
                         GeneralCriterion.V_SHAPE_INDIFFERENCE,
                         GeneralCriterion.LEVEL, GeneralCriterion.USUAL,
                         GeneralCriterion.GAUSSIAN]
criteria_directions = [Direction.MIN, Direction.MAX, Direction.MIN, Direction.MIN, Direction.MIN, Direction.MAX]

preference_thresholds = [None, 30, 5, 6, None, None]
indifference_thresholds = [10, None, 0.5, 1, None, None]
standard_deviations = [None, None, None, None, None, 5]


alternatives_performances = pd.DataFrame(data=alternatives_performances, index=alternatives, columns=criteria)
preference_thresholds = pd.Series(data=preference_thresholds, index=criteria)
indifference_thresholds = pd.Series(data=indifference_thresholds, index=criteria)
standard_deviations = pd.Series(data=standard_deviations, index=criteria)
generalized_criteria = pd.Series(data=generalized_criterion, index=criteria)
criteria_directions = pd.Series(data=criteria_directions, index=criteria)
