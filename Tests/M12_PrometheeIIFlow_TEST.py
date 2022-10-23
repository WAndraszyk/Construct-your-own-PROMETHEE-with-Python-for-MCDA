from ModularParts.flows.M12_PrometheeIIFlow import PrometheeIIFlow
from M9_PrometheeOutrankingFlows_TEST import *

flow = PrometheeIIFlow(positive_flows, negative_flows).calculate_PrometheeIIFlow()

print("----------------PROMETHEEII FLOW----------------")
for i in flow:
    print(i)
