from ModularParts.M3_PrometheePreference import PreferenceFunction
from ModularParts.M4_PrometheePreferenceReinforcedPreference import PreferenceFunction as M4_PreferenceFunction

alternatives_performances = [[35.8, 67.0, 19.7, 0.0, 0.0, 5.0, 4.0],
                             [16.4, 14.5, 59.8, 7.5, 5.2, 5.0, 3.0],
                             [35.8, 24.0, 64.9, 2.1, 4.5, 5.0, 4.0],
                             [20.6, 61.7, 75.7, 3.6, 8.0, 5.0, 3.0],
                             [11.5, 17.1, 57.1, 4.2, 3.7, 5.0, 2.0],
                             [22.4, 25.1, 49.8, 5.0, 7.9, 5.0, 3.0],
                             [23.9, 34.5, 48.9, 2.5, 8.0, 5.0, 3.0],
                             [29.9, 44.0, 57.8, 1.7, 2.5, 5.0, 4.0],
                             [8.7, 5.4, 27.4, 4.5, 4.5, 5.0, 2.0],
                             [25.7, 29.7, 46.8, 4.6, 3.7, 4.0, 2.0],
                             [21.2, 24.6, 64.8, 3.6, 8.0, 4.0, 2.0],
                             [18.3, 31.6, 69.3, 2.8, 3.0, 4.0, 3.0],
                             [20.7, 19.3, 19.7, 2.2, 4.0, 4.0, 2.0],
                             [9.9, 3.5, 53.1, 8.5, 5.3, 4.0, 2.0],
                             [10.4, 9.3, 80.9, 1.4, 4.1, 4.0, 2.0],
                             [17.7, 19.8, 52.8, 7.9, 6.1, 4.0, 4.0],
                             [14.8, 15.9, 27.9, 5.4, 1.8, 4.0, 2.0],
                             [16.0, 14.7, 53.5, 6.8, 3.8, 4.0, 4.0],
                             [11.7, 10.0, 42.1, 12.2, 4.3, 5.0, 2.0],
                             [11.0, 4.2, 60.8, 6.2, 4.8, 4.0, 2.0],
                             [15.5, 8.5, 56.2, 5.5, 1.8, 4.0, 2.0],
                             [13.2, 9.1, 74.1, 6.4, 5.0, 2.0, 2.0],
                             [9.1, 4.1, 44.8, 3.3, 10.4, 3.0, 4.0],
                             [12.9, 1.9, 65.0, 14.0, 7.5, 4.0, 3.0],
                             [5.9, -27.7, 77.4, 16.6, 12.7, 3.0, 2.0],
                             [16.9, 12.4, 60.1, 5.6, 5.6, 3.0, 2.0],
                             [16.7, 13.1, 73.5, 11.9, 4.1, 2.0, 2.0],
                             [14.6, 9.7, 59.5, 6.7, 5.6, 2.0, 2.0],
                             [5.1, 4.9, 28.9, 2.5, 46.0, 2.0, 2.0],
                             [24.4, 22.3, 32.8, 3.3, 5.0, 3.0, 4.0],
                             [29.5, 8.6, 41.8, 5.2, 6.4, 2.0, 3.0],
                             [7.3, -64.5, 67.5, 30.1, 8.7, 3.0, 3.0],
                             [23.7, 31.9, 63.6, 12.1, 10.2, 3.0, 2.0],
                             [18.9, 13.5, 74.5, 12.0, 8.4, 3.0, 3.0],
                             [13.9, 3.3, 78.7, 14.7, 10.1, 2.0, 2.0],
                             [-13.3, -31.1, 63.0, 21.2, 29.1, 2.0, 1.0],
                             [6.2, -3.2, 46.1, 4.8, 10.5, 2.0, 1.0],
                             [4.8, -3.3, 71.1, 8.6, 11.6, 2.0, 2.0],
                             [0.1, -9.6, 42.5, 12.9, 12.4, 1.0, 1.0],
                             [13.6, 9.1, 76.0, 17.1, 10.3, 1.0, 1.0]]

alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'a10', 'a11',
                'a12', 'a13', 'a14', 'a15', 'a16', 'a17', 'a18', 'a19', 'a20', 'a21',
                'a22', 'a23', 'a24', 'a25', 'a26', 'a27', 'a28', 'a29', 'a30', 'a31',
                'a32', 'a33', 'a34', 'a35', 'a36', 'a37', 'a38', 'a39', 'a40']

profiles_performances = [[4.0, 0.0, 65.0, 28.0, 12.0, 2.0, 3.0],
                         [10.0, 10.0, 45.0, 23.0, 8.0, 3.0, 4.0],
                         [15.0, 20.0, 40.0, 18.0, 4.0, 4.0, 5.0],
                         [25.0, 30.0, 35.0, 10.0, 0.0, 5.0, 6.0]]

profiles = ['b12', 'b23', 'b34', 'b45']

criteria = ['g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7']
criteria_weights = [0.073, 0.370, 0.228, 0.109, 0.156, 0.020, 0.044]
preference_thresholds = [2, 4, 3, 3, 3, 0, 0]
indifference_thresholds = [1, 4, 1, 0, 1, 0, 0]
reinforced_preferences = [4, 8, 6, 6, 6, 3, 3]
reinforcement_factors = [1.2, 1.2, 1.2, 1.3, 1.1, 1.1, 1.1]
srf_criteria_rank = ['g6', None, 'g7', None, None, None, 'g1', ['g4', 'g5'], None, 'g3', 'g2']
srf_criteria_weight_ratio = 2
standard_deviations = [None, None, None, None, None, None, None]
# cost -> 0
# gain -> 1

criteria_directions = [1, 1, 0, 0, 0, 1, 1]

criteria_ranks = [5, 1, 2, 4, 3, 7, 6]

generalized_criteria = [PreferenceFunction.V_SHAPE_INDIFFERENCE, PreferenceFunction.U_SHAPE,
                        PreferenceFunction.LEVEL, PreferenceFunction.V_SHAPE,
                        PreferenceFunction.V_SHAPE_INDIFFERENCE, PreferenceFunction.USUAL, PreferenceFunction.USUAL]

M4_generalized_criteria = [M4_PreferenceFunction.V_SHAPE_INDIFFERENCE, M4_PreferenceFunction.U_SHAPE,
                           M4_PreferenceFunction.LEVEL, M4_PreferenceFunction.V_SHAPE,
                           M4_PreferenceFunction.V_SHAPE_INDIFFERENCE, M4_PreferenceFunction.USUAL,
                           M4_PreferenceFunction.USUAL]
