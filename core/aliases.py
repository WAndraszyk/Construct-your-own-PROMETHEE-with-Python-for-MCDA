from typing import Union, List

import pandas as pd

NumericValue = Union[int, float]
PreferenceTable = Union[pd.DataFrame, tuple[pd.DataFrame]]
Id = str

Alternative = Id
CategoryProfile = Id
Criterion = Id

PerformanceTable = pd.DataFrame  # Alternatives performances or Category Profiles performances
PreferencesTable = pd.DataFrame
PreferencePartialTable = Union[pd.DataFrame, tuple[pd.DataFrame]]
Preferences = tuple[PreferenceTable]
FlowsTable = pd.DataFrame
NetOutrankingFlows = pd.Series
DMsTable = pd.DataFrame
RankedCriteria = pd.Series
DeviationsTable = List[Union[List[List[NumericValue]], List[List[List[NumericValue]]]]]