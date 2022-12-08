from typing import Callable, Union

from pandas import DataFrame

NumericValue = float
Value = Union[float, str]

PerformanceTable = DataFrame

Function = Callable[[Value], Value]
NumericFunction = Callable[[NumericValue], NumericValue]

# from typing import Union, List, Tuple
#
import pandas as pd
#
# NumericValue = Union[int, float]
# PreferenceTable = Union[pd.DataFrame, Tuple[pd.DataFrame]]
# Id = str
#
# Alternative = Id
# CategoryProfile = Id
# Criterion = Id
#
# PerformanceTable = pd.DataFrame  # Alternatives performances or Category Profiles performances
# PreferencesTable = pd.DataFrame
# PreferencePartialTable = Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]
# Preferences = Tuple[pd.DataFrame, pd.DataFrame]
# FlowsTable = pd.DataFrame
# NetOutrankingFlows = pd.Series
# DMsTable = pd.DataFrame
# RankedCriteria = pd.Series
#
# DeviationsTable = List[Union[List[List[NumericValue]], List[List[List[NumericValue]]]]]
