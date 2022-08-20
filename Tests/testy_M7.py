from ModularParts.M3_PrometheePreference import (PrometheePreference, PreferenceFunction)
from ModularParts.M1_SurrogateWeights import SurrogateWeights
from ModularParts.M9_PrometheeOutrankingFlows import PrometheeOutrankingFlows
from ModularParts.M11_PrometheeIRanking import PrometheeIRanking
from ModularParts.M13_PrometheeIIIFlow import PrometheeIIIFlow
from ModularParts.M7_PrometheeVeto import PrometheeVeto

kryteria = ['G1', 'G2']
rankingKryteriow = ['G2', 'G1']
directions = [0, 1]
p_param = [4, 0.5]
q_param = [0.4, 5]
s_param = [3, 3]
v_param = [3, 3]
weights = SurrogateWeights(rankingKryteriow, kryteria).rankSum()
print(weights)
warianty = ['a1', 'a2', 'a3']
#      G1   G2
ap = [[10, 12],  # a1
      [12.5, 13],  # a2
      [15, 3]]  # a3
# TEST M7 SAME WARIANTY
print("--------Test modułu M7 dla samych wariantów----------")

veto, partialVeto = PrometheeVeto(kryteria, ap, weights,
                                  v_param, directions).computeVetoIndices()
print("partial veto", partialVeto)
print("Veto : ", veto)

# TEST M7 PROFILE
print("--------Test modułu M7 dla profili ----------")

profile = ['b1', 'b2']
#      G1  G2
pp = [[9.5, 11],  # b1
      [14, 13]]  # b2


veto, partialVeto = PrometheeVeto( kryteria, ap, weights,
                                  v_param, directions, categories_profiles=True, profile_performance_table=pp, full_veto=False).computeVetoIndices()
print("partial veto", partialVeto)
print("Veto : ", veto)
