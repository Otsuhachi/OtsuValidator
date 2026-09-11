__all__ = ("Comparable",)


from typing import Protocol


# 比較演算子を持つことを示すためのProtocol
class Comparable(Protocol):
    # <
    def __lt__(self, other: object) -> bool: ...

    # ==
    def __eq__(self, other: object) -> bool: ...
