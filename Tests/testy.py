from ModularParts.M3_PrometheePreference import (PrometheePreference, PreferenceFunction)
from ModularParts.M1_SurrogateWeights import SurrogateWeights
from ModularParts.M9_PrometheeOutrankingFlows import PrometheeOutrankingFlows
from ModularParts.M11_PrometheeIRanking import PrometheeIRanking


kryteria = ['G1', 'G2']
rankingKryteriow = ['G2', 'G1']
directions = [0, 1]
generalized_criteria = [PreferenceFunction.U_SHAPE, PreferenceFunction.V_SHAPE]
p_param = [4, 0.5]
q_param = [0.4, 5]
s_param = [3, 3]

weights = SurrogateWeights(rankingKryteriow, kryteria).rankSum()
print("wagi : ", weights)
print(generalized_criteria)

warianty = ['a1', 'a2', 'a3']
#      G1   G2
ap = [[10, 12],  # a1
      [11, 13],  # a2
      [12, 14]]  # a3

# TEST M3 SAME WARIANTY
print("--------Test modułu M3 dla samych wariantów----------")

aggregatedPI, partialPref = PrometheePreference(warianty, kryteria, ap, weights,
                                                p_param, q_param, s_param, generalized_criteria,
                                                directions).computePreferenceIndices()
print("partial pref", partialPref)
print("preferencje : ", aggregatedPI)

positiveFlow, negativeFlow = PrometheeOutrankingFlows(warianty, aggregatedPI).calculate_flows()
print(positiveFlow, negativeFlow)

pairs = PrometheeIRanking(warianty, positiveFlow, negativeFlow).calculate_ranking()
print(pairs)

# TEST M3 PROFILE
print("--------Test modułu M3 dla wariantów i profili----------")
#      G1   G2
ap = [[10, 12],  # a1
      [11, 13],  # a2
      [12, 14]]  # a3

profile = ['b1', 'b2']
#      G1  G2
pp = [[11, 11],  # b1
      [14, 13]]  # b2

aggregatedPI, partialPref = PrometheePreference(warianty, kryteria, ap, weights,
                                                p_param, q_param, s_param, generalized_criteria,
                                                directions, profile, pp).computePreferenceIndices()
print("partial pref", partialPref)
print("preferencje : ", aggregatedPI)

positiveFlow, negativeFlow = PrometheeOutrankingFlows(warianty, aggregatedPI).calculate_flows()
print(positiveFlow, negativeFlow)

# RANKINGS ARE NOT SUPPOSED TO ACCEPT category_profiles AND CANNOT BUILD RANKINGS WITH category_profiles
# pairs = PrometheeIRanking(warianty, positiveFlow, negativeFlow).calculate_ranking()
# print(pairs)
