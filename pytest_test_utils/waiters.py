from time import perf_counter, sleep
from typing import Callable, TypeVar

_T = TypeVar("_T")


class TimedOutError(Exception):
    pass


def wait_until(pred: Callable[[], _T], timeout: float, pause: float = 1) -> _T:
    start = perf_counter()
    while (perf_counter() - start) < timeout:
        value = pred()
        if value:
            return value
        sleep(pause)
    raise TimedOutError("Timeout reached while waiting")
