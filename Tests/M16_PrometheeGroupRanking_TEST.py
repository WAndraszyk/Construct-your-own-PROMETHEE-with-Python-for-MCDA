from ModularParts.preference.M3_PrometheePreference import PrometheePreference
from ModularParts.weights.M1_SurrogateWeights import SurrogateWeights
from ModularParts.flows.M9_PrometheeOutrankingFlows import PrometheeOutrankingFlows
from ModularParts.flows.M16_PrometheeGroupRanking import PrometheeGroupRanking
from DecisionProblemData import *


proper_criteria_ranks = [x for _, x in sorted(zip(criteria_ranks, criteria), reverse=True)]

sur_weights = SurrogateWeights(criteria=criteria, criteria_rank=proper_criteria_ranks)
calculated_criteria_weights = sur_weights.rankOrderCentroid()  # doesn't work properly


## M-3 Preferences
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
print(preferences)


## M-9 Flows
pro_out_flows = PrometheeOutrankingFlows(alternatives=alternatives,
                                         preferences=preferences,
                                         category_profiles=profiles)

positive_flows, negative_flows = pro_out_flows.calculate_flows()

print(positive_flows)

dummy_flows_1 = dummy_flows_2 = [0.923, 0.47934925, 0.471, 0.58775, 0.471375, 0.55225, 0.64475, 0.72275, 0.54075, 0.58625, 0.49025,
               0.52925, 0.66475, 0.252775, 0.30775, 0.475125, 0.6699, 0.4865, 0.383775, 0.36475, 0.4064, 0.316,
               0.30445, 0.16725, 0.08865075, 0.382725, 0.301525, 0.3613, 0.431325, 0.64225, 0.4392, 0.06225, 0.4631,
               0.273, 0.1358, 0.0721, 0.194, 0.09447575, 0.16725, 0.205325]

dummy_flows_1 = [round(0.9*flow, 2) for flow in dummy_flows_1]
print(dummy_flows_1)

dummy_flows_2 = [round(1.06*flow, 2) for flow in dummy_flows_2]
print(dummy_flows_2)

# M16
flows_list = [positive_flows, dummy_flows_1, dummy_flows_2]
DMs_weights = [1.5, 2, 1.3]

prom_group_ranking = PrometheeGroupRanking(alternatives=alternatives,
                                           flows=flows_list,
                                           weightsDMs=DMs_weights)

aggregated_new_flows, weighted_new_flows = prom_group_ranking.calculate_group_ranking()

print(aggregated_new_flows)
print(weighted_new_flows)




