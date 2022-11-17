from typing import Union, List, Tuple

import pandas as pd

NumericValue = Union[int, float]
PreferenceTable = Union[pd.DataFrame, Tuple[pd.DataFrame]]
Id = str

Alternative = Id
CategoryProfile = Id
Criterion = Id

PerformanceTable = pd.DataFrame  # Alternatives performances or Category Profiles performances
PreferencesTable = pd.DataFrame

PreferencePartialTable = Union[pd.DataFrame, Tuple[pd.DataFrame]]
Preferences = Tuple[PreferenceTable]

FlowsTable = pd.DataFrame
NetOutrankingFlows = pd.Series
DMsTable = pd.DataFrame
RankedCriteria = pd.Series

DeviationsTable = List[Union[List[List[NumericValue]], List[List[List[NumericValue]]]]]

