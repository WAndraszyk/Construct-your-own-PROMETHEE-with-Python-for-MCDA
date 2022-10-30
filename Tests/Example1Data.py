import pandas as pd

from core.preference_commons import PreferenceFunction
from modular_parts.weights.M2_SRFWeights import  calculate_srf_weights
alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'a10', 'a11',
                'a12', 'a13', 'a14', 'a15', 'a16', 'a17', 'a18', 'a19', 'a20']

criteria = ['g1', 'g2', 'g3', 'g4', 'g5', 'g6']

alternatives_performances = [[2, 47, 2, 3, 1, 0],
                             [2, 3, 2, 4, 4, 0],
                             [5, 63, 1, 5, 1, 0],
                             [1, 92, 3, 5, 5, 1],
                             [4, 13, 2, 4, 2, 0],
                             [5, 5, 3, 5, 1, 0],
                             [1, 27, 3, 2, 5, 1],
                             [4, 28, 0, 5, 3, 0],
                             [3, 73, 0, 2, 1, 1],
                             [4, 3, 2, 2, 3, 0],
                             [3, 75, 2, 4, 3, 1],
                             [3, 40, 2, 1, 3, 0],
                             [2, 48, 1, 3, 3, 0],
                             [5, 57, 1, 0, 2, 1],
                             [1, 16, 3, 4, 2, 1],
                             [3, 22, 0, 3, 4, 0],
                             [4, 90, 2, 0, 0, 0],
                             [4, 33, 2, 1, 5, 1],
                             [1, 95, 3, 1, 3, 0],
                             [2, 18, 1, 4, 2, 1]]

budget = [27, 29, 20, 34, 32, 22, 34, 30, 28, 21, 32, 37, 26, 16, 13, 32, 35, 20, 40, 39]

srf_criteria_rank = ['g1', None, ['g3', 'g6'], None, None, 'g2', 'g5', None, 'g4']

ratio = 5
weights = pd.Series(data=[0.06,0.2,0.11,0.29,0.23,0.11], index=criteria)

generalized_criterion = [PreferenceFunction.V_SHAPE, PreferenceFunction.GAUSSIAN, PreferenceFunction.U_SHAPE,
                         PreferenceFunction.V_SHAPE_INDIFFERENCE, PreferenceFunction.U_SHAPE,
                         PreferenceFunction.U_SHAPE]

# cost -> 0
# gain -> 1
criteria_directions = [1, 1, 1, 1, 1, 1]

indifference_thr = [0, None, 0, 1, 0, 0]

preference_thr = [2, None, 0, 2, 0, 0]

sigma_thr = [None, 4, None, None, None, None]

veto_thr = [None, 40, None, 4, None, None]

reinforced_preference_thr = [None, None, 2, 3, 3, None]

reinforced_factor = [None, None, 1.2, 1.5, 1.3, None]


alternatives_performances = pd.DataFrame(data=alternatives_performances, index=alternatives, columns=criteria)
preference_thresholds = pd.Series(data=preference_thr, index=criteria)
indifference_thresholds = pd.Series(data=indifference_thr, index=criteria)
standard_deviations = pd.Series(data=sigma_thr, index=criteria)
generalized_criteria = pd.Series(data=generalized_criterion, index=criteria)
criteria_directions = pd.Series(data=criteria_directions, index=criteria)

