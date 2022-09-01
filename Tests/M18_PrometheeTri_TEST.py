from ModularParts.M3_PrometheePreference import PrometheePreference
from ModularParts.M18_PrometheeTri import PrometheeTri
from DecisionProblemData import *

## M-3 Preferences
### alternatives vs profiles preferences

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
                               decimal_place=3)

preferences, partial_preferences = pro_pref.computePreferenceIndices()  # rounding doesn't work properly, rest looks fine


### profiles vs profiles preferences
pro_pro_pref = PrometheePreference(alternatives=profiles, criteria=criteria,
                                   alternatives_performances=profiles_performances,
                                   weights=criteria_weights,
                                   p_list=preference_thresholds,
                                   q_list=indifference_thresholds,
                                   s_list=standard_deviations,
                                   generalized_criteria=generalized_criteria,
                                   directions=criteria_directions,
                                   decimal_place=3)
profiles_preferences, profiles_partial_preferences = pro_pro_pref.computePreferenceIndices()

# M-18 PrometheeTri

prom_tri = PrometheeTri(alternatives=alternatives,
                        categories=['c1', 'c2', 'c3', 'c4'],
                        category_profiles=profiles,
                        criteria=criteria,
                        criteria_weights=criteria_weights,
                        partial_preferences=partial_preferences,
                        profiles_partial_preferences=profiles_partial_preferences,
                        assign_to_better_class=True,
                        use_marginal_value=True)

sorted_alternatives = prom_tri.calculate_sorted_alternatives()

print(sorted_alternatives)

