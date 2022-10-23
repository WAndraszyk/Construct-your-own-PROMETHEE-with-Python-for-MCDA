from ModularParts.choice.M23_PrometheeV import PrometheeV
from core.constraint import Constraint, Relation
from M12_PrometheeIIFlow_TEST import *

constraints = [Constraint(budget, Relation.LT, 150)]

chosen_alternatives = PrometheeV(alternatives, flow, constraints).compute_decision()

print("------------------------DECISION-------------")
print(chosen_alternatives)
