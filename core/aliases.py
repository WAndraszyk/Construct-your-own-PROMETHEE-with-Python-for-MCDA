from typing import Callable, Union

from pandas import DataFrame

NumericValue = Union[float, int]
Value = Union[float, str]

PerformanceTable = DataFrame

Function = Callable[[Value], Value]
NumericFunction = Callable[[NumericValue], NumericValue]
