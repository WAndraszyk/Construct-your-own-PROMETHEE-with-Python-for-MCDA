from ModularParts.M4_PrometheePreferenceReinforcedPreference \
    import (PrometheePreferenceReinforcedPreference, PreferenceFunction)
from ModularParts.M1_SurrogateWeights import SurrogateWeights
from ModularParts.M9_PrometheeOutrankingFlows import PrometheeOutrankingFlows
from ModularParts.M11_PrometheeIRanking import PrometheeIRanking

kryteria = ['G1', 'G2']
rankingKryteriow = ['G2', 'G1']
directions = [0, 1]
generalized_criteria = [PreferenceFunction.U_SHAPE, PreferenceFunction.V_SHAPE]
p_param = [4, 0.5]
q_param = [0.4, 5]
rp_param = [1.5, 1.5]
omega_param = [1.2, 1.2]

weights = SurrogateWeights(rankingKryteriow, kryteria).rankSum()
print("wagi : ", weights)
print("generalized criteria: ", generalized_criteria)

warianty = ['a1', 'a2', 'a3']
#      G1   G2
ap = [[10, 12],  # a1
      [11, 13],  # a2
      [12, 14]]  # a3

# TEST M4 SAME WARIANTY
print("--------Test modułu M4 dla samych wariantów----------")

aggregatedPI, partialPref = PrometheePreferenceReinforcedPreference(warianty, kryteria, ap, weights,
                                                                    p_param, q_param, generalized_criteria,
                                                                    directions, rp_param,
                                                                    omega_param).computePreferenceIndices()
print("partial pref", partialPref)
print("preferencje : ", aggregatedPI)

positiveFlow, negativeFlow = PrometheeOutrankingFlows(warianty, aggregatedPI).calculate_flows()
print("positive flow: ", positiveFlow, "negative flow: ", negativeFlow)

pairs = PrometheeIRanking(warianty, positiveFlow, negativeFlow).calculate_ranking()
print("Ranking M11_PrometheeIRanking:", pairs)

# TEST M4 PROFILE
print("--------Test modułu M4 dla wariantów i profili----------")
#      G1   G2
ap = [[10, 12],  # a1
      [11, 13],  # a2
      [12, 14]]  # a3

profile = ['b1', 'b2']
#      G1  G2
pp = [[11, 11],  # b1
      [14, 13]]  # b2

aggregatedPI, partialPref = PrometheePreferenceReinforcedPreference(warianty, kryteria, ap, weights,
                                                                    p_param, q_param, generalized_criteria,
                                                                    directions, rp_param, omega_param, profile,
                                                                    pp).computePreferenceIndices()
print("partial pref", partialPref)
print("preferencje : ", aggregatedPI)

positiveFlow, negativeFlow = PrometheeOutrankingFlows(warianty, aggregatedPI).calculate_flows(True)
print("positive flow: ", positiveFlow, "negative flow: ", negativeFlow)

pairs = PrometheeIRanking(warianty, positiveFlow, negativeFlow).calculate_ranking()
print(pairs)
