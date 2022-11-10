import pandas as pd

alternatives = [f"a{i}" for i in range(1, 13)]
alternatives_performances = pd.DataFrame([[84, 83, 12, 7, 85], [72, 78, 7, 5, 70],
                                          [70, 82, 7, 7, 80], [70, 68, 20, 25, 75],
                                          [70, 95, 15, 5, 95], [90, 85, 30, 32, 85],
                                          [80, 75, 15, 7, 80], [86, 90, 10, 5, 85],
                                          [92, 85, 30, 26, 90], [70, 65, 25, 28, 60],
                                          [75, 85, 30, 32, 65], [92, 90, 8, 5, 90]], index=alternatives)

profiles = [f"b{i}" for i in range(1, 4)]
profiles_performances = pd.DataFrame([[65, 70, 25, 25, 65], [80, 80, 18, 15, 75], [90, 90, 8, 7, 90]], index=profiles)

criteria = [f"g{i}" for i in range(1, 6)]
preference_thresholds = pd.Series([10, 10, 7, 8, 10], index=criteria)
indifference_thresholds = pd.Series([0, 0, 0, 0, 5], index=criteria)


