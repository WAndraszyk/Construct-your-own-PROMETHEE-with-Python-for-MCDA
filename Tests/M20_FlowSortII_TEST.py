from ModularParts.M3_PrometheePreference import PrometheePreference
from ModularParts.M9_PrometheeOutrankingFlows import PrometheeOutrankingFlows
from ModularParts.M12_PrometheeIIFlow import PrometheeIIFlow
from ModularParts.M20_FlowSortII import FlowSortII, CompareProfiles
from DecisionProblemData import *

proper_criteria_ranks = [x for _, x in sorted(zip(criteria_ranks, criteria), reverse=True)]

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

preferences, partial_preferences = pro_pref.computePreferenceIndices()

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

positive_flows, negative_flows = pro_out_flows.calculate_flows()

### profiles flows
pro_pro_out_flows = PrometheeOutrankingFlows(alternatives=profiles,
                                             preferences=profiles_preferences)
profiles_positive_flows, profiles_negative_flows = pro_pro_out_flows.calculate_flows()

## M-12 PrometheIIFlow
### alternatives flows
pro2_flows = PrometheeIIFlow(positive_flow=positive_flows, negative_flow=negative_flows)

flows = pro2_flows.calculate_PrometheeIIFlow()

### profiles flows
profiles_pro2_flows = PrometheeIIFlow(positive_flow=profiles_positive_flows, negative_flow=profiles_negative_flows)

profiles_flows = profiles_pro2_flows.calculate_PrometheeIIFlow()

## M-20 FlowSortII
flow_sort_2 = FlowSortII(alternatives=alternatives,
                         categories=['c1', 'c2', 'c3', 'c4', 'c5'],
                         category_profiles=profiles,
                         profiles_performances=profiles_performances,
                         criteria=(preference_thresholds, criteria_directions),
                         flows=(flows, profiles_flows),
                         comparison_with_profiles=CompareProfiles.BOUNDARY_PROFILES)

sorted_alternatives = flow_sort_2.calculate_sorted_alternatives()

print(sorted_alternatives)
