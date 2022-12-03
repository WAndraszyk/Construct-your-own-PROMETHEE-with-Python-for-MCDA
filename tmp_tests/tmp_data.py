import pandas as pd

from core.enums import Direction, PreferenceFunction

alternatives = [f"a{i}" for i in range(1, 6)]
profiles = [f"r{i}" for i in range(1, 4)]
categories = [f"C{i}" for i in range(1, 4)]
criteria = [f"g{i}" for i in range(1, 6)]

criteria_ranking = pd.Series([4, 3, 5, 1, 3], index=criteria)
criteria_ratio = 3

dms_weights = pd.Series([1, 2], index=['DM1', 'DM2'])

alternatives_performances = pd.DataFrame([[25, 65, 30, 15, 65],
                                          [30, 65, 30, 10, 65],
                                          [50, 30, 60, 55, 50],
                                          [65, 20, 50, 65, 45],
                                          [70, 10, 15, 70, 10]],
                                         index=alternatives, columns=criteria)

profiles_performances = pd.DataFrame([[20, 60, 25, 20, 60],
                                      [40, 35, 40, 50, 40],
                                      [60, 10, 55, 60, 15]],
                                     index=profiles, columns=criteria)

profiles_performances_DM2 = pd.DataFrame([[20, 65, 25, 30, 60],
                                          [35, 30, 40, 45, 30],
                                          [50, 20, 55, 65, 20]],
                                         index=profiles, columns=criteria)

criteria_directions = pd.Series([Direction.MAX, Direction.MIN, Direction.MAX,
                                 Direction.MAX, Direction.MIN], index=criteria)
generalized_criteria = pd.Series([PreferenceFunction.V_SHAPE, PreferenceFunction.U_SHAPE,
                                  PreferenceFunction.V_SHAPE_INDIFFERENCE, PreferenceFunction.LEVEL,
                                  PreferenceFunction.V_SHAPE_INDIFFERENCE], index=criteria)
criteria_weights = pd.Series([0.35, 0.25, 0.18, 0.07, 0.15], index=criteria)

preference_thresholds = pd.Series([10, 0, 10, 8, 10], index=criteria)
indifference_thresholds = pd.Series([0, 15, 5, 0, 5], index=criteria)
standard_deviations = pd.Series([0, 0, 0, 0, 0], index=criteria)

reinforced_preference_thresholds = pd.Series([15, 20, 15, 12, 15], index=criteria)
reinforcement_factors = pd.Series([1.2, 1.2, 1.2, 1.2, 1.2], index=criteria)

# interactions = pd.DataFrame([[]], index=criteria, columns=criteria)

tau = 2  # ?

# v_list = pd.Series([], index=criteria)
