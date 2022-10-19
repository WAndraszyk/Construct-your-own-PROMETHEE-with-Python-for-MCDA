from ModularParts.M1_SurrogateWeights import SurrogateWeights
import pandas as pd
from ModularParts.M5_PrometheePreferenceWithInteractions import PrometheePreferenceWithInteractions

criteria = ['g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7']
ranking = SurrogateWeights(ranked_criteria=pd.Series(data=[7, 1, 3, 2, 4, 5, 6], index=criteria)).rank_sum()
print(pd.Series(data=[7, 1, 3, 2, 4, 5, 6], index=criteria))
print(ranking)

ranking = SurrogateWeights(ranked_criteria=pd.Series(data=[7, 1, 3, 2, 4, 5, 6], index=criteria)).equal_weights()
print(pd.Series(data=[7, 1, 3, 2, 4, 5, 6], index=criteria))
print(ranking)

ranking = SurrogateWeights(ranked_criteria=pd.Series(data=[1, 2, 3, 4, 5, 6, 7], index=criteria)).reciprocal_of_ranks()
print(ranking)

ranking = SurrogateWeights(ranked_criteria=pd.Series(data=[1, 2, 3, 4, 5, 6, 7], index=criteria)).rank_order_centroid()
print(ranking)
