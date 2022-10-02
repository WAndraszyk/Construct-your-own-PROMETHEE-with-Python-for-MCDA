from PandasModularParts.pd_M1_SurrogateWeights import SurrogateWeights
import pandas as pd
from ModularParts.M5_PrometheePreferenceWithInteractions import PrometheePreferenceWithInteractions
from PandasModularParts.pd_M3_PrometheePreference import PrometheePreference
from Tests.DecisionProblemData import *

criteria = ['g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7']
ranking = SurrogateWeights(ranked_criteria=pd.Series(data=[7, 1, 3, 2, 4, 5, 6], index=criteria)).rank_sum()
print(pd.Series(data=[7, 1, 3, 2, 4, 5, 6], index=criteria))
print(ranking)
preference, partial_preference = PrometheePreference(alternatives_performances=
                                                     pd.DataFrame(data=alternatives_performances, index=alternatives,
                                                                  columns=criteria), weights=ranking,
                                                     criteria_features=df_criteria
                                                     ).computePreferenceIndices()

print("----------------------PREFERENCE--------------")
for i in preference:
    print(i)
