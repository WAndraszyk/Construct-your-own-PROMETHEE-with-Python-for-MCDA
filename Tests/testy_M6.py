from ModularParts.M3_PrometheePreference import (PrometheePreference, PreferenceFunction)
from ModularParts.M1_SurrogateWeights import SurrogateWeights
from ModularParts.M6_PrometheeDiscordance import PrometheeDiscordance

kryteria = ['G1', 'G2']
rankingKryteriow = ['G2', 'G1']
directions = [0, 1]
generalized_criteria = [PreferenceFunction.U_SHAPE, PreferenceFunction.V_SHAPE]
p_param = [4, 0.5]
q_param = [0.4, 5]
s_param = [3, 3]

weights = SurrogateWeights(rankingKryteriow, kryteria).rankSum()
print("wagi : ", weights)
print("generalized criteria: ", generalized_criteria)

warianty = ['a1', 'a2', 'a3']
#      G1   G2
ap = [[10, 12],  # a1
      [11, 13],  # a2
      [12, 14]]  # a3

# TEST M6 SAME WARIANTY
print("--------Test modułu M6 dla samych wariantów----------")

aggregatedPI, partialPref = PrometheePreference(warianty, kryteria, ap, weights,
                                                p_param, q_param, s_param, generalized_criteria,
                                                directions).computePreferenceIndices()
print("partial preferences: ", partialPref)
print("preferences : ", aggregatedPI)

discordance, partial_discordance = PrometheeDiscordance(2, partialPref).compute_discordance(1.5)
print("partial discordance: ", partial_discordance)
print("discordance: ", discordance)

overall_preference = PrometheeDiscordance(2, partialPref).compute_discordance(1.5, aggregatedPI)
print("overall preferences: ", overall_preference)

# TEST M6 PROFILE
print("--------Test modułu M6 dla wariantów i profili----------")

profile = ['b1', 'b2']
#      G1  G2
pp = [[11, 11],  # b1
      [14, 13]]  # b2

aggregatedPI, partialPref = PrometheePreference(warianty, kryteria, ap, weights,
                                                p_param, q_param, s_param, generalized_criteria,
                                                directions, profile, pp).computePreferenceIndices()
print("partial preferences", partialPref)
print("preferences: ", aggregatedPI)

discordance, partial_discordance = PrometheeDiscordance(2, partialPref, True).compute_discordance(1.25)
print("partial discordance: ", partial_discordance)
print("discordance: ", discordance)

overall_preference = PrometheeDiscordance(2, partialPref, True).compute_discordance(1.5, aggregatedPI)
print("overall preferences: ", overall_preference)
