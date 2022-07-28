from ModularParts.PrometheePreferenceReinforcedPreference \
    import (PrometheePreferenceReinforcedPreference, PreferenceFunction)
from ModularParts.SurrogateWeights import SurrogateWeights
from ModularParts.PrometheeOutrankingFlows import PrometheeOutrankingFlows
from ModularParts.PrometheeIRanking import PrometheeIRanking

warianty = ['Pierwszy', 'Drugi', 'Trzeci']
kryteria = ['G1', 'G2']
ap = [[10, 12],
      [11, 13],
      [12, 14]]
rankingKryteriow = ['G2', 'G1']
directions = [0, 1]
generalized_criteria = [PreferenceFunction.U_SHAPE, PreferenceFunction.V_SHAPE]

weights = SurrogateWeights(rankingKryteriow, kryteria).rankSum()
print("wagi : ", weights)
print(generalized_criteria)

p_param = [4, 0.5]
q_param = [0.4, 5]
rp_param = [1.5, 1.5]
omega_param = [1.2, 1.2]

aggregatedPI, partialPref = PrometheePreferenceReinforcedPreference(warianty, kryteria, ap, weights,
                                                                    p_param, q_param, generalized_criteria,
                                                                    directions, rp_param,
                                                                    omega_param).computePreferenceIndices()
print("partial pref", partialPref)
print("preferencje : ", aggregatedPI)

positiveFlow, negativeFlow = PrometheeOutrankingFlows(warianty, aggregatedPI).calculate_flows()
print(positiveFlow, negativeFlow)

pairs = PrometheeIRanking(warianty, positiveFlow, negativeFlow).calculate_ranking()
print(pairs)
