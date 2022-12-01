from tmp_data import *
from core.enums import ScoringFunction, ScoringFunctionDirection

from modular_parts.weights import *
from modular_parts.preference import *
from modular_parts.flows import *
from modular_parts.alternatives_profiles import *
from modular_parts.sorting import *

surrogate_ranking = rank_order_centroid(criteria_ranking)
print(15 * "~" + "M1" + 15 * "~" + "\n", surrogate_ranking)

print(15 * "~" + "M2" + 15 * "~" + "\n", calculate_srf_weights(criteria_ranking, criteria_ratio))

preferences = compute_preference_indices(alternatives_performances, preference_thresholds, indifference_thresholds,
                                         standard_deviations, generalized_criteria, criteria_directions,
                                         criteria_weights)[0]

print(15 * "~" + "M3" + 15 * "~" + "\n", preferences)

reinforced_preferences = compute_reinforced_preference(alternatives_performances, preference_thresholds,
                                                       indifference_thresholds, generalized_criteria,
                                                       criteria_directions, reinforced_preference_thresholds,
                                                       reinforcement_factors, criteria_weights)[0]

print(15 * "~" + "M4" + 15 * "~" + "\n", reinforced_preferences)

outranking_flows = calculate_prometheeI_outranking_flows(preferences)
print(15 * "~" + "M8" + 15 * "~" + "\n", outranking_flows)

net_flow_score = calculate_net_flows_score(preferences, ScoringFunction.MAX, ScoringFunctionDirection.IN_FAVOR,
                                           avoid_same_scores=True)

net_flow_score2 = calculate_net_flows_score(preferences, ScoringFunction.SUM, ScoringFunctionDirection.AGAINST,
                                            avoid_same_scores=True)

print(15 * "~" + "M10_1" + 15 * "~" + "\n", net_flow_score)
print(15 * "~" + "M10_2" + 15 * "~" + "\n", net_flow_score2)

dms_flows = pd.DataFrame({'DM1': net_flow_score.values,
                          'DM2': net_flow_score2.values}, index=net_flow_score.index)

aggregated_flows = calculate_promethee_group_ranking(dms_flows, dms_weights)
print(15 * "~" + "M11" + 15 * "~" + "\n", aggregated_flows)

# TODO Odpalić dla M20, M21, M21x, M22
