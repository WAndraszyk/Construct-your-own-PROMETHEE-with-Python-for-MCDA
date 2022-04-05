import PrometheePreference as PP
import SurrogateWeights as SW
import PrometheeOutrankingFlows as POF
import PrometheeIRanking as PI_Rank

warianty = ['Pierwszy', 'Drugi', 'Trzeci']
kryteria = ['G1', 'G2']
ap = [[10, 12],
      [11, 13],
      [12, 14]]
rankingKryteriow = ['G2', 'G1']

weights = SW.SurrogateWeights(rankingKryteriow, kryteria).rankSum()
print("wagi : " ,weights)
aggregatedPI, partialPref = PP.PrometheePreference(warianty,kryteria,ap,weights).computePreferenceIndices()
print("partial pref", partialPref)
print("preferencje : ", aggregatedPI)

positiveFlow, negativeFlow = POF.PrometheeOutrankingFlows(warianty, aggregatedPI).calculate_flows()
pairs = PI_Rank.PrometheeIRanking(warianty,positiveFlow, negativeFlow).calculate_ranking()
print(pairs)