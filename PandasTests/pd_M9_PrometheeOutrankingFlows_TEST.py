import pandas as pd
import numpy as np
from ModularParts.flows.M9_PrometheeOutrankingFlows import PrometheeOutrankingFlows

# for alternatives vs alternatives
n = 5
alternatives = pd.Index([f"a{i}" for i in range(1, n+1)])
alternatives_preferences = pd.DataFrame(np.random.rand(n, n), index=alternatives, columns=alternatives)

alternatives_flows = PrometheeOutrankingFlows(alternatives_preferences).calculate_flows()

# for alternatives vs profiles
a = 5
p = 3
profiles = pd.Index([f"p{i}" for i in range(1, p+1)])
alternatives_profiles_preferences = pd.DataFrame(np.random.rand(a, p), index=alternatives, columns=profiles)
profiles_alternatives_preferences = pd.DataFrame(np.random.rand(p, a), index=profiles, columns=alternatives)

alternatives_profiles_preferences = PrometheeOutrankingFlows((alternatives_profiles_preferences,
                                                              profiles_alternatives_preferences)).calculate_flows()

print("------------------------OUTRANKING FLOWS---------------")
print("Alternatives flows: \n", alternatives_flows)
print('')
print("Alternatives vs profiles flows: \n", alternatives_profiles_preferences)
