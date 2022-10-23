from ModularParts.preference.M3_PrometheePreference import PrometheePreference
from ModularParts.weights.M1_SurrogateWeights import SurrogateWeights
from ModularParts.flows.M9_PrometheeOutrankingFlows import PrometheeOutrankingFlows
from ModularParts.sorting.M17_PromSort import PromSort
from DecisionProblemData import *


proper_criteria_ranks = [x for _, x in sorted(zip(criteria_ranks, criteria), reverse=True)]

sur_weights = SurrogateWeights(criteria=criteria, criteria_rank=proper_criteria_ranks)
calculated_criteria_weights = sur_weights.rankOrderCentroid()  # doesn't work properly


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

## M-9 Flows
### alternatives flows
pro_out_flows = PrometheeOutrankingFlows(alternatives=alternatives,
                                         preferences=preferences,
                                         category_profiles=profiles)

positive_flows, negative_flows = pro_out_flows.calculate_flows()  # works fine

### profiles flows
pro_pro_out_flows = PrometheeOutrankingFlows(alternatives=profiles,
                                             preferences=profiles_preferences)
profiles_positive_flows, profiles_negative_flows = pro_pro_out_flows.calculate_flows()


## M-17 PromSort
prom_sort = PromSort(alternatives=alternatives,
                     categories=['c1', 'c2', 'c3', 'c4', 'c5'],
                     category_profiles=profiles,
                     profiles_performances=profiles_performances,
                     criteria=(preference_thresholds, criteria_directions),
                     negative_flows=(negative_flows, profiles_negative_flows),
                     positive_flows=(positive_flows, profiles_positive_flows),
                     cut_point=0,
                     assign_to_better_class=True)

sorted_alternatives = prom_sort.calculate_sorted_alternatives()

print(sorted_alternatives)

