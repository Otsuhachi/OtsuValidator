__all__ = (
    "FLOAT_INT",
    "Comparable",
    "StrPath",
)


import pathlib
from typing import Any, Protocol

type StrPath = str | pathlib.Path
type FLOAT_INT = float | int


# 比較演算子を持つことを示すためのProtocol
class Comparable(Protocol):
    # <
    def __lt__(self, other: Any) -> bool: ...
    # ==
    def __eq__(self, other: Any) -> bool: ...
