from typing import Union

import pandas as pd

NumericValue = Union[int, float]

Id = str

Alternative = Id
CategoryProfile = Id
Criterion = Id


PerformanceTable = pd.DataFrame  # Alternatives performances or Category Profiles performances
CriteriaFeatures = pd.DataFrame
PreferencesTable = pd.DataFrame
FlowsTable = pd.DataFrame
DMsTable = pd.DataFrame


