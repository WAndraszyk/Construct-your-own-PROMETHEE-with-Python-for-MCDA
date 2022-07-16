from ModularParts.M3_PrometheePreference import (PrometheePreference, PreferenceFunction)
from ModularParts.M1_SurrogateWeights import SurrogateWeights
from ModularParts.M9_PrometheeOutrankingFlows import PrometheeOutrankingFlows
from ModularParts.M11_PrometheeIRanking import PrometheeIRanking

warianty = ['Pierwszy', 'Drugi', 'Trzeci']
kryteria = ['G1', 'G2']
ap = [[10, 12],
      [11, 13],
      [12, 14]]
rankingKryteriow = ['G2', 'G1']
directions = [0, 1]
generalized_criteria = [PreferenceFunction.U_SHAPE, PreferenceFunction.V_SHAPE]
p_param = [4, 0.5]
q_param = [0.4, 5]
s_param = [3, 3]

weights = SurrogateWeights(rankingKryteriow, kryteria).rankSum()
print("wagi : ", weights)
print(generalized_criteria)
aggregatedPI, partialPref = PrometheePreference(warianty, kryteria, ap, weights,
                                                p_param, q_param, s_param, generalized_criteria,
                                                directions).computePreferenceIndices()
print("partial pref", partialPref)
print("preferencje : ", aggregatedPI)

positiveFlow, negativeFlow = PrometheeOutrankingFlows(warianty, aggregatedPI).calculate_flows()
print(positiveFlow, negativeFlow )

pairs = PrometheeIRanking(warianty, positiveFlow, negativeFlow).calculate_ranking()
print(pairs)
