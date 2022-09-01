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
                               p_list=preference_threshold,
                               q_list=indifference_threshold,
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
                                   p_list=preference_threshold,
                                   q_list=indifference_threshold,
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


## M-12 PrometheIIFlow



## M-20 FlowSortII
