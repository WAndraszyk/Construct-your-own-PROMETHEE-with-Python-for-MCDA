from typing import Callable, Union

from pandas import DataFrame

NumericValue = float
Value = Union[float, str]

PerformanceTable = DataFrame

Function = Callable[[Value], Value]
NumericFunction = Callable[[NumericValue], NumericValue]
