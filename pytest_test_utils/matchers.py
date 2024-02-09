import collections.abc
import re
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    AnyStr,
    Pattern,
    Tuple,
    Union,
)

if TYPE_CHECKING:
    from _pytest.python_api import ApproxBase


class regex:
    """Special class to eq by matching regex"""

    def __init__(
        self,
        pattern: Union[AnyStr, Pattern[AnyStr]],
        flags: Union[int, re.RegexFlag] = 0,
    ) -> None:
        self._regex: Pattern[AnyStr] = re.compile(pattern, flags)  # type: ignore[arg-type]

    def __repr__(self) -> str:
        flags = self._regex.flags & ~32  # 32 is default
        flags_repr = f", {flags}" if flags else ""
        return f"regex(r'{self._regex.pattern!s}'{flags_repr})"

    def __eq__(self, other: Any) -> bool:
        assert isinstance(other, (str, bytes))
        return bool(self._regex.search(other))  # type: ignore[arg-type]


class any:
    """Equals to anything.

    A way to ignore parts of data structures on comparison"""

    def __repr__(self) -> str:
        return "any"

    def __eq__(self, other: Any) -> bool:
        return True


class MatcherDict:
    """Special class to eq by matching only presented dict keys"""

    # Implementation notes:
    # - can't inherit from dict because that makes D() == M.dict() to not call
    #   our __eq__, if D is a subclass of a dict
    # - should not call itself dict or use dict in repr because it creates
    #   confusing error messages (shadowing python builtins is bad anyway)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.d = dict(*args, **kwargs)

    def __len__(self) -> int:
        return len(self.d)

    def __repr__(self) -> str:
        inner = ", ".join(f"{k}={repr(v)}" for k, v in self.d.items())
        return f"M.dict({inner})"

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, collections.abc.Mapping)
        return all(other.get(name) == v for name, v in self.d.items())


class unordered:
    """Compare list contents, but do not care about ordering.

    (E.g. sort lists first, then compare.)
    If you care about ordering, then just compare lists directly."""

    def __init__(self, *items: Any) -> None:
        self.items = items

    def __repr__(self) -> str:
        inner = ", ".join(map(repr, self.items))
        return f"unordered({inner})"

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, collections.abc.Iterable)
        return sorted(self.items) == sorted(other)


class attrs:
    def __init__(self, **attribs: Any) -> None:
        self.attribs = attribs

    def __repr__(self) -> str:
        inner = ", ".join(f"{k}={repr(v)}" for k, v in self.attribs.items())
        return f"attrs({inner})"

    def __eq__(self, other: Any) -> bool:
        # Unforturnately this doesn't work with classes with slots
        # self.__class__ = other.__class__
        return all(getattr(other, name) == v for name, v in self.attribs.items())


class any_of:
    def __init__(self, *items: Any) -> None:
        self.items = sorted(items)

    def __repr__(self) -> str:
        inner = ", ".join(map(repr, self.items))
        return f"any_of({inner})"

    def __eq__(self, other: object) -> bool:
        return other in self.items


class instance_of:
    def __init__(self, expected_type: Union[Any, Tuple[Any, ...]]) -> None:
        self.expected_type = expected_type

    def __repr__(self) -> str:
        if isinstance(self.expected_type, tuple):
            inner = f"({', '.join(t.__name__ for t in self.expected_type)})"
        else:
            inner = self.expected_type.__name__
        return f"{self.__class__.__name__}({inner})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.expected_type)


def approx(expected, rel=None, abs=None, nan_ok: bool = False) -> "ApproxBase":  # type: ignore[no-untyped-def]
    if isinstance(expected, datetime):
        from ._approx import approx_datetime

        return approx_datetime(expected, abs=abs)

    import pytest

    return pytest.approx(expected, rel=rel, abs=abs, nan_ok=nan_ok)


class Matcher(attrs):
    """Special class to eq by existing attrs.
    The purpose is to simplify asserts containing objects, i.e.:

    assert (
        result.errors ==
        [M(message=M.re("^Something went wrong:"), extensions={"code": 523})]
    )

    Here all the structures like lists and dicts are followed as usual both
    outside and inside a mather object. These could be freely intermixed.
    """

    any = any()
    dict = MatcherDict

    @staticmethod
    def attrs(**attribs: Any) -> attrs:
        return attrs(**attribs)

    @staticmethod
    def regex(
        pattern: Union[AnyStr, Pattern[AnyStr]],
        flags: Union[int, re.RegexFlag] = 0,
    ) -> regex:
        return regex(pattern, flags=flags)

    re = regex

    @staticmethod
    def unordered(*items: Any) -> unordered:
        return unordered(*items)

    @staticmethod
    def any_of(*items: Any) -> any_of:
        return any_of(*items)

    @staticmethod
    def instance_of(expected_type: Union[Any, Tuple[Any, ...]]) -> instance_of:
        return instance_of(expected_type)

    @staticmethod
    def approx(expected, rel=None, abs=None, nan_ok: bool = False) -> "ApproxBase":  # type: ignore[no-untyped-def]
        return approx(expected, rel=rel, abs=abs, nan_ok=nan_ok)
