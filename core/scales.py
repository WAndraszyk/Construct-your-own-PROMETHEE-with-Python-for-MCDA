from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List, Union, cast

import numpy as np

from .aliases import Function, NumericValue, Value
from .functions import FuzzyNumber, Interval


def numeric_value(value: Union[NumericValue, FuzzyNumber]) -> NumericValue:
    """Convert value to numeric.

    Used to keep numeric values as is, and convert
    :class:`functions.FuzzyNumber` to numerical value.

    :param value:
    :return:
    """
    return value.centre_of_gravity if isinstance(value, FuzzyNumber) else value


class PreferenceDirection(Enum):
    """Enumeration of MCDA preference directions."""

    MIN = auto()
    MAX = auto()

    @classmethod
    def has_value(cls, x: "PreferenceDirection") -> bool:
        """Check if value is in enumeration.

        :param x:
        :return:
        """
        return x in cls

    @classmethod
    def content_message(cls) -> str:
        """Return list of items and their values.

        :return:
        """
        s = ", ".join(f"{item}: {item.value}" for item in cls)
        return "PreferenceDirection only has following values " + s


class Scale(ABC):
    """Basic abstract class for MCDA scale."""

    @abstractmethod
    def __contains__(self, x: Value) -> bool:  # pragma: nocover
        """Check if values are inside scale.

        :param x:
        :return:
        """
        pass

    @abstractmethod
    def range(self, nb: int = None) -> List[Value]:  # pragma: nocover
        """Return range of value from scale.

        :param nb: number of values to return
        :return:
        """
        pass

    @abstractmethod
    def transform_to(
        self, x: Value, target_scale: "Scale" = None
    ) -> Value:  # pragma: nocover
        """Transform value from this scale to target scale.

        :param x:
        :param target_scale:
        :return:
        """
        pass

    def normalize(self, x: Value) -> NumericValue:
        """Normalize value.

        :param x:
        :return: normalized value
        """
        return cast(NumericValue, self.transform_to(x, get_normalized_scale()))

    def denormalize(self, x: NumericValue) -> Value:
        """Denormalize value.

        :param x: normalized value
        :return: denormalized value
        """
        return get_normalized_scale().transform_to(cast(Value, x), self)


class NominalScale(Scale):
    """This class implements a MCDA nominal scale.

    :param labels:
    """

    def __init__(self, labels: List[Value]):
        """Constructor method"""
        Scale.__init__(self)
        self.labels = labels

    def __contains__(self, x: Value) -> bool:
        """Check if values are inside scale.

        :param x:
        :return:
        """
        return x in self.labels

    def range(self, nb: int = None) -> List[Value]:
        """Return range of value from scale.

        :param nb: number of values to return (always ignored here)
        :return:
        """
        return self.labels

    def transform_to(self, x: Value, target_scale: Scale = None) -> Value:
        """Transform value from this scale to target scale.

        :param x:
        :param target_scale:
        :return:
        :raise ValueError:
            * if value `x` is outside this scale
            * if `target_scale` is not set
        :raise TypeError:
            if `target_scale` is neither :class:`QualitativeScale` nor
            :class:`NominalScale`
        """
        if x not in self:
            raise ValueError(f"label outside scale: {x}")
        if target_scale is None:
            raise ValueError("non-specified target scale")
        if isinstance(target_scale, NominalScale):
            return target_scale.labels[target_scale.labels.index(x)]
        raise TypeError("cannot transform from nominal to quantitative scale")


class QuantitativeScale(Scale, Interval):
    """Class for quantitative scale.

    :param dmin: min boundary of scale
    :param dmax: max boundary of scale
    :param preference_direction: scale preference direction
    :raises ValueError:
        * if `dmax` smaller than `dmin`
        * if `preference_direction` is unknown
    """

    def __init__(
        self,
        dmin: NumericValue,
        dmax: NumericValue,
        preference_direction: PreferenceDirection = PreferenceDirection.MAX,
    ):
        """Constructor method"""
        Interval.__init__(self, dmin, dmax)
        if not PreferenceDirection.has_value(preference_direction):
            raise ValueError(PreferenceDirection.content_message())
        self.preference_direction = preference_direction

    def __contains__(self, x: Value) -> bool:
        """Check if values are inside scale.

        :param x:
        :return:
        """
        return self.inside(cast(NumericValue, x))

    def range(self, nb: int = None) -> List[Value]:
        """Return range of value from scale.

        :param nb: number of values to return
        :return:
        """
        nb = 2 if nb is None else nb
        return cast(
            List[Value], np.linspace(self.dmin, self.dmax, nb).tolist()
        )

    def _normalize_value(self, x: NumericValue) -> NumericValue:
        """Normalize numeric value.

        :param x:
        :return:

        .. note::
            `preference_direction` is taken into account, so preferred
            value is always bigger.
        """
        if self.preference_direction == PreferenceDirection.MIN:
            return 1 - Interval.normalize(self, x)
        return Interval.normalize(self, x)

    def _denormalize_value(self, x: NumericValue) -> NumericValue:
        """Denormalize normalized numeric value.

        :param x:
        :return:

        .. note::
            `preference_direction` is taken into account, so preferred
            normalized value must always be bigger.
        """
        if self.preference_direction == PreferenceDirection.MIN:
            return cast(NumericValue, Interval.denormalize(self, 1 - x))
        return cast(NumericValue, Interval.denormalize(self, x))

    def transform_to(self, x: Value, target_scale: Scale = None) -> Value:
        """Transform value from this scale to target scale.

        :param x:
        :param target_scale:
        :return:
        :raise ValueError:
            * if value `x` is outside this scale
            * if `target_scale` is not set
        :raise TypeError:
            if target_scale is neither :class:`QuantitativeScale` nor
            :class:`QualitativeScale`

        .. note:: `preference_direction` attributes are taken into account
        """
        if x not in self:
            raise ValueError(f"value outside scale: {x}")
        if target_scale is None:
            raise ValueError("non-specified target scale")
        _x = cast(NumericValue, x)
        if isinstance(target_scale, QualitativeScale):
            return target_scale.label_from_value(
                target_scale._denormalize_value(self._normalize_value(_x))
            )
        if isinstance(target_scale, QuantitativeScale):
            return target_scale._denormalize_value(self._normalize_value(_x))
        raise TypeError("cannot transform from quantitative to nominal scale")

    def normalize(self, x: Value) -> NumericValue:
        """Normalize value.

        :param x:
        :return: normalized value

        .. note:: `preference_direction` attributes is taken into account
        """
        return Scale.normalize(self, x)

    def denormalize(self, x: NumericValue) -> Value:
        """Denormalize value.

        :param x: normalized value
        :return: denormalized value

        .. note:: `preference_direction` attributes is taken into account
        """
        return Scale.denormalize(self, x)

    def is_better(self, x: Value, y: Value) -> bool:
        """Check if x is better than y according to this scale.

        :param x:
        :param y:
        :return:
        """
        _x, _y = cast(NumericValue, x), cast(NumericValue, y)
        return (
            _x > _y
            if self.preference_direction == PreferenceDirection.MAX
            else _x < _y
        )


_NORMALIZED_SCALE = QuantitativeScale(0, 1)


def get_normalized_scale():
    return _NORMALIZED_SCALE


class QualitativeScale(QuantitativeScale, NominalScale):
    """This class implements a MCDA qualitative scale.

    :param labels:
    :param values:
    :param preference_direction: scale preference direction
    :param dmin: min boundary of scale (inferred from `values` if not set)
    :param dmax: max boundary of scale (inferred from `values` if not set)
    :raises ValueError:
        * if number of `labels` and `values` differs
        * if `preference_direction` is unknown
        * if at least one value is outside the bounds
    :raises TypeError:
        * if `values` contains non-numeric values

    .. warning::
        This scale contains `labels` not `values`. `values` are only here to
        define a corresponding quantitative scale for default scale
        transformation. After calling :meth:`transform_to` with no associated
        scale, the data is no longer considered inside the qualitative scale.

    .. todo::
        this scale is quantitative but has a quantitative scale as an
        attribute. Find out how to best type cast it.
    """

    def __init__(
        self,
        labels: List[Value],
        values: List[NumericValue],
        preference_direction: PreferenceDirection = PreferenceDirection.MAX,
        dmin: NumericValue = None,
        dmax: NumericValue = None,
    ):
        """Constructor method"""
        if len(labels) != len(values):
            raise ValueError(
                "QualitativeScale must have same number of labels"
                " and values"
            )
        NominalScale.__init__(self, labels)
        for value in values:
            if type(value) not in [
                int,
                float,
                np.float,
                np.int,
            ]:
                raise TypeError(
                    "QualitativeScale must have numeric values."
                    f"Got: {type(value)}"
                )
        dmin = min(values) if dmin is None else dmin
        dmax = max(values) if dmax is None else dmax
        for value in values:
            if value < dmin or value > dmax:
                raise ValueError(
                    f"value '{value}' is outside the defined bounds "
                    f"[{dmin}, {dmax}]"
                )
        self.values = values
        QuantitativeScale.__init__(
            self,
            dmin,
            dmax,
            preference_direction,
        )
        self.__quantitative = QuantitativeScale(
            dmin,
            dmax,
            preference_direction,
        )

    @property
    def quantitative(
        self,
    ) -> QuantitativeScale:  # Property used to hide setter
        """Quantitative scale extracted from current qualitative scale."""
        return self.__quantitative

    def __contains__(self, x: Value) -> bool:
        """Check if label is inside scale.

        :param x:
        :return:
        """
        return NominalScale.__contains__(self, x)

    def range(self, nb: int = None) -> List[Value]:
        """Return range of value from scale.

        :param nb: number of values to return (always ignored here)
        :return:
        """
        return NominalScale.range(self, nb)

    def transform_to(self, x: Value, target_scale: Scale = None) -> Value:
        """Transform value from this scale to target scale.

        :param x:
        :param target_scale:
        :return:
        :raise ValueError: if value `x` is outside this scale
        :raise TypeError: if `target_scale` has unknown type

        .. note::
            `preference_direction` attributes are taken into account when
            rescaling to a :class:`QuantitativeScale`
        """
        if x not in self:
            raise ValueError(f"label outside scale: {x}")
        target_scale = (
            self.quantitative if target_scale is None else target_scale
        )
        if isinstance(target_scale, NominalScale):
            return target_scale.labels[target_scale.labels.index(x)]
        if isinstance(target_scale, QuantitativeScale):
            value = self.values[self.labels.index(x)]
            return target_scale._denormalize_value(
                self._normalize_value(value)
            )
        raise TypeError(
            f"unrecognized scale type for scale: {target_scale}"
        )  # pragma: nocover

    def label_from_value(self, x: Value) -> Value:
        """Transform value to this scale.

        :param x:
        :raises ValueError: if `x` corresponds to no label
        :return: label associated to given value
        """
        if x not in self.values:
            raise ValueError(f"value outside scale: {x}")
        _x = cast(NumericValue, x)
        return self.labels[self.values.index(_x)]

    def is_better(self, x: Value, y: Value) -> bool:
        """Check if x is better than y according to this scale.

        :param x:
        :param y:
        :return:
        """
        return self.quantitative.is_better(
            self.transform_to(x), self.transform_to(y)
        )


class FuzzyScale(QualitativeScale):
    """This class implements a MCDA fuzzy qualitative scale.

    :param labels:
    :param fuzzy:
    :param preference_direction: scale preference direction
    :param dmin: min boundary of scale (inferred from `values` if not set)
    :param dmax: max boundary of scale (inferred from `values` if not set)
    :raises ValueError:
        * if number of `labels` and `fuzzy` differs
        * if `preference_direction` is unknown
        * if at least one fuzzy number is outside the bounds
    :raises TypeError:
        * if `fuzzy` contains non-fuzzy numbers
    """

    def __init__(
        self,
        labels: List[Value],
        fuzzy: List[FuzzyNumber],
        preference_direction: PreferenceDirection = PreferenceDirection.MAX,
        dmin: NumericValue = None,
        dmax: NumericValue = None,
    ):
        values = []
        for fz in fuzzy:
            if type(fz) is not FuzzyNumber:
                raise TypeError("fuzzy scales can only contains fuzzy numbers")
        dmin = min(fz.abscissa[0] for fz in fuzzy) if dmin is None else dmin
        dmax = max(fz.abscissa[-1] for fz in fuzzy) if dmax is None else dmax
        for fz in fuzzy:
            if fz.abscissa[0] < dmin or fz.abscissa[-1] > dmax:
                raise ValueError(
                    "fuzzy number sets must be within the defined bounds "
                    f"[{dmin}, {dmax}]"
                )
            values.append(fz.centre_of_gravity)
        QualitativeScale.__init__(
            self, labels, values, preference_direction, dmin, dmax
        )
        self.fuzzy = fuzzy

    def defuzzify(self, method: str = "centre_of_gravity"):
        """Defuzzify all fuzzy numbers using given method.

        :param method:
            method used to defuzzify
            (from :class:`mcda.core.functions.FuzzyNumber` numeric methods)
        """
        for i, fz in enumerate(self.fuzzy):
            self.values[i] = getattr(fz, method)

    def is_fuzzy_partition(self) -> bool:
        """Test whether the scale define a fuzzy partition.

        :return:
        """
        indexes = sorted(range(len(self.labels)), key=lambda i: self.values[i])
        fuzzy_sets = [self.fuzzy[i] for i in indexes]
        for i in range(len(fuzzy_sets) - 1):
            for j in range(2):
                if (
                    fuzzy_sets[i].abscissa[j + 2]
                    != fuzzy_sets[i + 1].abscissa[j]
                ):
                    return False
        return True

    def similarity(
        self, fuzzy1: FuzzyNumber, fuzzy2: FuzzyNumber
    ) -> NumericValue:
        """Returns similarity between both fuzzy numbers w.r.t this scale.

        :param fuzzy1:
        :param fuzzy2:
        :return:

        .. note:: implementation based on :cite:p:`isern2010ulowa`
        """
        a = [self.quantitative.normalize(v) for v in fuzzy1.abscissa]
        b = [self.quantitative.normalize(v) for v in fuzzy2.abscissa]
        res = [2 - abs(aa - bb) for aa, bb in zip(a, b)]
        prod = 1.0
        for r in res:
            prod *= r
        return prod ** (1 / 4) - 1

    def fuzziness(self, fuzzy: FuzzyNumber) -> NumericValue:
        """Returns the fuzziness of given fuzzy number w.r.t this scale.

        :param fuzzy:
        :return:
        """
        return self.quantitative.normalize(
            (
                fuzzy.abscissa[1]
                + fuzzy.abscissa[3]
                - fuzzy.abscissa[0]
                - fuzzy.abscissa[2]
            )
            / 2
        )

    def specificity(self, fuzzy: FuzzyNumber) -> NumericValue:
        """Returns the specificity of given fuzzy number w.r.t this scale.

        :param fuzzy:
        :return:
        """
        return 1 - self.quantitative.normalize(fuzzy.area)

    def ordinal_distance(self, a: Value, b: Value) -> NumericValue:
        """Returns the ordinal distance between the labels
        (sorted by defuzzified values).

        :param a:
        :param b:
        :return:
        :raises ValueError: if `a` or `b` is not inside the scale
        """
        if a not in self or b not in self:
            raise ValueError("both labels must be inside the fuzzy scale")
        labels = sorted(self.labels, key=lambda v: self.transform_to(v))
        return abs(labels.index(a) - labels.index(b))


class ScaledFunction:
    """This class implements functions with an input definition domain.

    The input definition domain is represented by a :class:`Scale` object.

    :param function:
    :param scale_input:
    """

    def __init__(self, function: Function, scale_input: Scale):
        self.function = function
        self.scale_input = scale_input

    def transform_to(self, scale: Scale) -> "ScaledFunction":
        """Return same function with a transformed definition domain.

        Transformation from input `scale` to attribute `scale_input` is
        composed to attribute `function` in order to create the new
        function.

        :param scale:
        :return:
        """
        return ScaledFunction(
            lambda x: self.function(scale.transform_to(x, self.scale_input)),
            scale,
        )

    def __call__(self, x: Value) -> Value:
        """Call function.

        :param x:
        :return:
        :raise ValueError: if `x` outside of `scale_input`
        """
        if x not in self.scale_input:
            raise ValueError(f"input is outside its scale: {x}")
        return self.function(x)


def is_better(x: Value, y: Value, scale: QuantitativeScale) -> bool:
    """Check if x is better than y according to this scale

    :param x:
    :param y:
    :param scale:
    :return:
    """
    return scale.is_better(x, y)


def is_better_or_equal(x: Value, y: Value, scale: QuantitativeScale) -> bool:
    """Check if x is better or equal to y according to this scale

    :param x:
    :param y:
    :param scale:
    :return:
    """
    return x == y or is_better(x, y, scale)
