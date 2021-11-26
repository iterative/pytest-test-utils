from typing import Any, Type


class ANY:
    def __init__(self, expected_type: Type[object]) -> None:
        self.expected_type: Type[object] = expected_type

    def __repr__(self) -> str:
        return "Any({self.expected_type.__name__})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.expected_type)
