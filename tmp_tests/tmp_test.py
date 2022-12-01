from tmp_data import *
from core.enums import ScoringFunction, ScoringFunctionDirection, CompareProfiles

from modular_parts.weights import *
from modular_parts.preference import *
from modular_parts.flows import *
from modular_parts.alternatives_profiles import *
from modular_parts.ranking import *
from modular_parts.sorting import *

surrogate_ranking = rank_order_centroid(criteria_ranking)
print(15 * "~" + "M1" + 15 * "~" + "\n", surrogate_ranking)

print(15 * "~" + "M2" + 15 * "~" + "\n", calculate_srf_weights(criteria_ranking, criteria_ratio))

# alternatives vs alternatives
preferences, partial_preferences = compute_preference_indices(alternatives_performances, preference_thresholds,
                                                              indifference_thresholds, standard_deviations,
                                                              generalized_criteria, criteria_directions,
                                                              criteria_weights)

# profiles vs profiles
profiles_preferences, profiles_partial_preferences = \
    compute_preference_indices(profiles_performances, preference_thresholds, indifference_thresholds,
                               standard_deviations, generalized_criteria, criteria_directions, criteria_weights)

# alternatives vs profiles
alter_prof_preferences, alter_prof_partial_preferences = \
    compute_preference_indices(alternatives_performances, preference_thresholds, indifference_thresholds,
                               standard_deviations, generalized_criteria, criteria_directions, criteria_weights,
                               profiles_performances)

print(15 * "~" + "M3.1" + 15 * "~" + "\n", preferences)
print(15 * "~" + "M3.2" + 15 * "~" + "\n", partial_preferences)

reinforced_preferences = compute_reinforced_preference(alternatives_performances, preference_thresholds,
                                                       indifference_thresholds, generalized_criteria,
                                                       criteria_directions, reinforced_preference_thresholds,
                                                       reinforcement_factors, criteria_weights)[0]

print(15 * "~" + "M4" + 15 * "~" + "\n", reinforced_preferences)

outranking_flows = calculate_prometheeI_outranking_flows(alter_prof_preferences)
profiles_outranking_flows = calculate_prometheeI_outranking_flows(profiles_preferences)

print(15 * "~" + "M8.1" + 15 * "~" + "\n", outranking_flows)
print(15 * "~" + "M8.2" + 15 * "~" + "\n", profiles_outranking_flows)

net_flow_score = calculate_net_flows_score(preferences, ScoringFunction.MAX, ScoringFunctionDirection.IN_FAVOR,
                                           avoid_same_scores=True)
profiles_net_flow_score = calculate_net_flows_score(profiles_preferences, ScoringFunction.MAX,
                                                    ScoringFunctionDirection.IN_FAVOR, avoid_same_scores=True)

net_flow_score2 = calculate_net_flows_score(preferences, ScoringFunction.SUM, ScoringFunctionDirection.AGAINST,
                                            avoid_same_scores=True)

print(15 * "~" + "M10_1" + 15 * "~" + "\n", net_flow_score)
print(15 * "~" + "M10_2" + 15 * "~" + "\n", net_flow_score2)

dms_flows = pd.DataFrame({'DM1': net_flow_score.values,
                          'DM2': net_flow_score2.values}, index=net_flow_score.index)

aggregated_flows = calculate_promethee_group_ranking(dms_flows, dms_weights)
print(15 * "~" + "M11" + 15 * "~" + "\n", aggregated_flows)

alternatives_profiles = calculate_alternatives_profiles(surrogate_ranking, partial_preferences)
print(15 * "~" + "M13" + 15 * "~" + "\n", alternatives_profiles)

promethee_i_rank = calculate_prometheeI_ranking(outranking_flows, weak_preference=False)
print(15 * "~" + "M14" + 15 * "~" + "\n", promethee_i_rank)

net_flow_score_rank = calculate_netflow_score_ranking(preferences, ScoringFunction.MAX,
                                                      ScoringFunctionDirection.IN_FAVOR, avoid_same_scores=True)
print(15 * "~" + "M16" + 15 * "~" + "\n", net_flow_score_rank)

prom_sort = calculate_promsort_sorted_alternatives(categories, outranking_flows, profiles_outranking_flows,
                                                   preference_thresholds, profiles_performances, criteria_directions,
                                                   cut_point=0, assign_to_better_class=True)
print(15 * "~" + "M17" + 15 * "~" + "\n", prom_sort)

promethee_tri = calculate_prometheetri_sorted_alternatives(categories, criteria_weights,
                                                           alter_prof_partial_preferences, profiles_partial_preferences)
print(15 * "~" + "M18" + 15 * "~" + "\n", promethee_tri)

flow_sort_i = calculate_flowsortI_sorted_alternatives(categories, profiles_performances, criteria_directions,
                                                      outranking_flows, profiles_outranking_flows,
                                                      CompareProfiles.CENTRAL_PROFILES)
print(15 * "~" + "M19" + 15 * "~" + "\n", flow_sort_i)

# TODO Odpalić dla M12, M20, M21, M22, M27
