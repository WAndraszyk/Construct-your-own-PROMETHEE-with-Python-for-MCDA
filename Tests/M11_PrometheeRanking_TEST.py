from ModularParts.M3_PrometheePreference import PrometheePreference
from ModularParts.M2_SRFWeights import SRFWeights
from ModularParts.M9_PrometheeOutrankingFlows import PrometheeOutrankingFlows
from ModularParts.M11_PrometheeIRanking import PrometheeIRanking
from DecisionProblemData import *

srf_weights = SRFWeights(criteria=criteria,
                         criteria_rank=srf_criteria_rank,
                         criteria_weight_ratio=srf_criteria_weight_ratio,
                         decimal_place=3)

calculated_criteria_weights = srf_weights.calculate_srf_weights()

print(calculated_criteria_weights)

## M-3 Preferences
pro_pref = PrometheePreference(alternatives=alternatives, criteria=criteria,
                               alternatives_performances=alternatives_performances,
                               weights=criteria_weights,
                               p_list=preference_thresholds,
                               q_list=indifference_thresholds,
                               s_list=standard_deviations,
                               generalized_criteria=generalized_criteria,
                               directions=criteria_directions,
                               decimal_place=3)

preferences, partial_preferences = pro_pref.computePreferenceIndices()

## M-9 Flows
pro_out_flows = PrometheeOutrankingFlows(alternatives=alternatives,
                                         preferences=preferences)

positive_flows, negative_flows = pro_out_flows.calculate_flows()  # works fine

## M-11 PrometheeI Ranking

promeetheI = PrometheeIRanking(alternatives=alternatives,
                               negative_flow=negative_flows,
                               positive_flow=positive_flows)

alternatives_ranking = promeetheI.calculate_ranking()

for pair in alternatives_ranking:
    print(pair)
