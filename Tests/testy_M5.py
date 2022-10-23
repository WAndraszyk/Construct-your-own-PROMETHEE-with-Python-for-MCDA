from ModularParts.preference.M5_PrometheePreferenceWithInteractions import PrometheePreferenceWithInteractions
from DecisionProblemData import *
from ModularParts.preference.M3_PrometheePreference import PrometheePreference

## M-3 Preferences
pro_pref = PrometheePreferenceWithInteractions(alternatives=alternatives, criteria=criteria,
                                               alternatives_performances=alternatives_performances,
                                               weights=criteria_weights,
                                               p_list=preference_thresholds,
                                               q_list=indifference_thresholds,
                                               s_list=standard_deviations,
                                               generalized_criteria=generalized_criteria,
                                               directions=criteria_directions,
                                               categories_profiles=profiles,
                                               profile_performance_table=profiles_performances,
                                               decimal_place=4,
                                               interactions=interactions)

preferences, partial_preferences = pro_pref.computePreferenceIndices()
print('M5')
print(preferences)
print(partial_preferences)

pro_pref = PrometheePreference(alternatives=alternatives, criteria=criteria,
                               alternatives_performances=alternatives_performances,
                               weights=criteria_weights,
                               p_list=preference_thresholds,
                               q_list=indifference_thresholds,
                               s_list=standard_deviations,
                               generalized_criteria=generalized_criteria,
                               directions=criteria_directions,
                               categories_profiles=profiles,
                               profile_performance_table=profiles_performances,
                               decimal_place=4)

preferences, partial_preferences = pro_pref.computePreferenceIndices()
print('M3')
print(preferences)
print(partial_preferences)
