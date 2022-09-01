from ModularParts.M3_PrometheePreference import PrometheePreference
from ModularParts.M4_PrometheePreferenceReinforcedPreference import PrometheePreferenceReinforcedPreference
from ModularParts.M21x_MultipleDMCriteriaNetFlows import MultipleDMUniNetFlows
from ModularParts.M21_FlowSortGDSS import FlowSortGDSS, CompareProfiles
from DecisionProblemData import *

# 1st DM
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

preferences_1, partial_preferences_1 = pro_pref.computePreferenceIndices()

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
profiles_preferences_1, profiles_partial_preferences_1 = pro_pro_pref.computePreferenceIndices()

# 2nd DM
## M-4 Preferences
### alternatives vs profiles preferences
pro_rein_pref = PrometheePreferenceReinforcedPreference(alternatives=alternatives,
                                                        criteria=criteria,
                                                        alternatives_performances=alternatives_performances,
                                                        weights=criteria_weights,
                                                        p_list=preference_thresholds,
                                                        q_list=indifference_thresholds,
                                                        generalized_criteria=M4_generalized_criteria,
                                                        directions=criteria_directions,
                                                        rp_list=reinforced_preferences,
                                                        omega_list=reinforcement_factors,
                                                        categories_profiles=profiles,
                                                        profile_performance_table=profiles_performances,
                                                        decimal_place=3)

preferences_2, partial_preferences_2 = pro_rein_pref.computePreferenceIndices()


### profiles vs profiles preferences
pro_pro_rein_pref = PrometheePreferenceReinforcedPreference(alternatives=profiles,
                                                            criteria=criteria,
                                                            alternatives_performances=profiles_performances,
                                                            weights=criteria_weights,
                                                            p_list=preference_thresholds,
                                                            q_list=indifference_thresholds,
                                                            generalized_criteria=M4_generalized_criteria,
                                                            directions=criteria_directions,
                                                            rp_list=reinforced_preferences,
                                                            omega_list=reinforcement_factors,
                                                            decimal_place=3)

profiles_preferences_2, profiles_partial_preferences_2 = pro_pro_rein_pref.computePreferenceIndices()


## 3rd DM
## M-4 Preferences
### alternatives vs profiles preferences
profiles_performances_2 = [[6.0, 3.0, 75.0, 26.0, 13.0, 2.0, 3.0],
                           [12.0, 9.0, 55.0, 21.0, 9.0, 3.0, 4.0],
                           [18.0, 15.0, 41.0, 14.0, 3.0, 4.0, 5.0],
                           [26.5, 22.0, 33.0, 8.0, 0.0, 6.0, 5.5]]

pro_rein_pref = PrometheePreferenceReinforcedPreference(alternatives=alternatives,
                                                        criteria=criteria,
                                                        alternatives_performances=alternatives_performances,
                                                        weights=criteria_weights,
                                                        p_list=preference_thresholds,
                                                        q_list=indifference_thresholds,
                                                        generalized_criteria=M4_generalized_criteria,
                                                        directions=criteria_directions,
                                                        rp_list=reinforced_preferences,
                                                        omega_list=reinforcement_factors,
                                                        categories_profiles=profiles,
                                                        profile_performance_table=profiles_performances_2,
                                                        decimal_place=3)

preferences_3, partial_preferences_3 = pro_rein_pref.computePreferenceIndices()



### profiles vs profiles preferences
pro_pro_rein_pref = PrometheePreferenceReinforcedPreference(alternatives=profiles,
                                                            criteria=criteria,
                                                            alternatives_performances=profiles_performances_2,
                                                            weights=criteria_weights,
                                                            p_list=preference_thresholds,
                                                            q_list=indifference_thresholds,
                                                            generalized_criteria=M4_generalized_criteria,
                                                            directions=criteria_directions,
                                                            rp_list=reinforced_preferences,
                                                            omega_list=reinforcement_factors,
                                                            decimal_place=3)

profiles_preferences_3, profiles_partial_preferences_3 = pro_pro_rein_pref.computePreferenceIndices()


# ---------------------------------------------------------------------------------
#M21x

DMs_preferences = [partial_preferences_1, partial_preferences_2, partial_preferences_3]
# DMs_preferences = [partial_preferences_1, partial_preferences_1, partial_preferences_1]


DMs_profiles_partial_preferences = [partial_preferences[1] for partial_preferences in DMs_preferences]  # P(r, a)
DMs_alternatives_partial_preferences = [partial_preferences[0] for partial_preferences in DMs_preferences]  # P(a, r)
DMs_profile_vs_profile_partial_preferences = [profiles_partial_preferences_1, profiles_partial_preferences_2,
                           profiles_partial_preferences_3]
# DMs_profile_vs_profile_partial_preferences = [profiles_partial_preferences_1, profiles_partial_preferences_1,
                           # profiles_partial_preferences_1]


M21_input = MultipleDMUniNetFlows(alternatives=alternatives,
                                  category_profiles=profiles,
                                  DMs_profiles_partial_preferences=DMs_profiles_partial_preferences,
                                  DMs_alternatives_partial_preferences=DMs_alternatives_partial_preferences,
                                  DMs_profile_vs_profile_partial_preferences=DMs_profile_vs_profile_partial_preferences,
                                  criteria_weights=criteria_weights)

alternative_global_net_flows, category_profiles_global_net_flows = M21_input.calculate_GDSS_flows()


#M21
DMs_profile_performances = [profiles_performances, profiles_performances, profiles_performances_2]
# DMs_profile_performances = [profiles_performances, profiles_performances, profiles_performances]

DMs_weights = [4, 3, 6]
# DMs_weights = [1, 1, 1]
flow_sort_gdss = FlowSortGDSS(alternatives=alternatives,
                              categories=['c1', 'c2', 'c3', 'c4', 'c5'],
                              category_profiles=profiles,
                              criteria=criteria_directions,
                              alternative_global_net_flows=alternative_global_net_flows,
                              category_profiles_global_net_flows=category_profiles_global_net_flows,
                              profiles_performances=DMs_profile_performances,
                              weights_DMs=DMs_weights,
                              comparison_with_profiles=CompareProfiles.BOUNDARY_PROFILES,
                              assign_to_better_class=True)

sorted_alternatives = flow_sort_gdss.calculate_sorted_alternatives()

print(sorted_alternatives[0])
print(sorted_alternatives[1])




