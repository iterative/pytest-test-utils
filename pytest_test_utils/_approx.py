from datetime import datetime, timedelta
from typing import Optional

from _pytest.python_api import ApproxBase

# pylint: disable=invalid-name


class approx_datetime(ApproxBase):  # pylint: disable=abstract-method
    """Perform approximate comparisons between datetime or timedelta."""

    default_tolerance = timedelta(seconds=1)
    expected: datetime
    abs: timedelta

    def __init__(
        self,
        expected: datetime,
        abs: Optional[timedelta] = None,  # pylint: disable=redefined-builtin
    ) -> None:
        """Initialize the approx_datetime with `abs` as tolerance."""
        assert isinstance(expected, datetime)
        abs = abs or self.default_tolerance
        assert abs >= timedelta(0), f"absolute tolerance can't be negative: {abs}"
        super().__init__(expected, abs=abs)

    def __repr__(self) -> str:  # pragma: no cover
        """String repr for approx_datetime, shown during failure."""
        return f"approx_datetime({self.expected!r} ± {self.abs!r})"

    def __eq__(self, actual: object) -> bool:
        """Checking for equality with certain amount of tolerance."""
        assert isinstance(actual, datetime), "expected type of datetime"
        return abs(self.expected - actual) <= self.abs
