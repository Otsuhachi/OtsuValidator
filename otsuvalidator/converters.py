import logging
import re
import warnings
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path
from typing import Any, Literal, override

from .bases import Converter
from .validators import VBool, VNumerical, VPath, VString, VTimedelta

__all__ = [
    "CBool",
    "CFloat",
    "CInt",
    "CNumber",
    "CNumerical",
    "CPath",
    "CString",
    "CTimedelta",
]


logger = logging.getLogger(__name__)


class CBool(VBool, Converter[Any, bool]):
    """VBoolの拡張バリデータ。

    一般にYes/Noとして解釈できる値に対し、bool変換を試みます。
    bool(value)とは異なる結果を返すことがあります。
    また、Trueにしたい値、Falseにしたい値をタプル形式で登録することでその通りに判定するようになります。

    str型, float型, int型に対応しています。
    また、str型はすべてstr.lowerされた後に判定されます。

    Trueに変換される値
        str型: 'true', 'yes', 'y', '1'
        int型: 1
        float型: 1.0

    Falseに変換される値
        str型: 'false', 'no', 'n', '0'
        int型: 0
        float型: 0.0
    """

    def __init__(
        self,
        true_data: tuple[Any, ...] | None = None,
        false_data: tuple[Any, ...] | None = None,
        checker: tuple[Callable[[Any], bool], ...] | None = None,
    ) -> None:
        """ユーザ定義のTrueにしたい値、Falseにしたい値を設定してバリデータを生成します。

        Args:
            true_data (Optional[Tuple[Any, ...]], optional): Trueにしたい値です。
            false_data (Optional[Tuple[Any, ...]], optional): Falseにしたい値です。
            checker (Optional[Tuple[Callable[[Any], bool], ...]], optional): 真偽判定用の関数です。
        """
        self.true_data = true_data
        self.false_data = false_data
        self.checker = checker

    def validate(self, value: Any) -> bool:
        # ユーザ定義で真偽確認
        tmp_value = value
        if (checker := self.true_data) is not None and value in checker:
            return super().validate(True)
        if (checker := self.false_data) is not None and value in checker:
            return super().validate(False)
        if (checker := self.checker) is not None:
            for c in checker:
                try:
                    tmp = c(tmp_value)
                    if tmp is None:
                        continue
                    tmp_value = tmp  # type: ignore
                except Exception:
                    continue
        # クラス定義で真偽を確認
        if (tv := type(tmp_value)) is bool:
            pass
        elif tv is str:
            tmp_value: str
            tmp_value = tmp_value.lower()
            if tmp_value in (yes := ("true", "yes", "y", "1", "1.0")):
                tmp_value = True  # type: ignore
            elif tmp_value in (no := ("false", "no", "n", "0", "0.0")):
                tmp_value = False  # type: ignore
            else:
                msg = "クラス定義の検証に失敗しました"
                logger.error(f"{msg}: {value}\n\tTrue: {yes}\n\tFalse: {no}")
                raise ValueError(f"{msg}。")
        elif tv is int:
            if tmp_value == 1:
                tmp_value = True  # type: ignore
            elif tmp_value == 0:
                tmp_value = False  # type: ignore
            else:
                msg = "1または0である必要があります"
                logger.error(f"{msg}: {tmp_value}")
                raise ValueError(f"{msg}。")
        elif tv is float:
            if tmp_value == 1.0:
                tmp_value = True  # type: ignore
            elif tmp_value == 0.0:
                tmp_value = False  # type: ignore
            else:
                msg = "1.0または0.0である必要があります"
                logger.error(f"{msg}: {tmp_value}")
                raise ValueError(f"{msg}。")
        else:
            msg = "Yes/Noとして解釈できる必要があります"
            logger.error(f"{msg}: {tmp_value}")
            raise TypeError(f"{msg}。")
        return super().validate(tmp_value)


class CNumerical[OutT: float | int](VNumerical[OutT], Converter[Any, OutT]):
    """
    数値を変換し、範囲を検証するコンバータの基底クラス。
    """

    def __init__(
        self,
        target_type: type[OutT] | None = None,
        min_val: OutT | None = None,
        max_val: OutT | None = None,
        *,
        type_strict: bool = False,
    ) -> None:
        super().__init__(min_val, max_val, type_strict=type_strict)
        self.target_type = target_type

    @override
    def validate(self, value: Any) -> OutT:
        """入力値を target_type に変換してから、VNumber の検証を実行する。"""
        # 1. 変換試行
        t_type = self.target_type
        try:
            if isinstance(value, bool):
                raise ValueError
            if t_type is None:
                # 動的判定モード
                f_val = float(value)
                converted = int(f_val) if f_val.is_integer() else f_val
            else:
                converted = tmp_value = float(value)
                if t_type is not float:
                    converted = t_type(tmp_value)
                if converted != tmp_value:
                    msg = "変換後の数値が元の数値と等価ではありません"
                    logger.error(f"{msg}: {value} -> {tmp_value}")
                    raise ValueError(f"{msg}。")
        except (TypeError, ValueError):
            type_name = t_type.__name__ if t_type else "number"
            msg = f"`{self.public_name}`を`{type_name}型`に変換できませんでした"
            logger.exception(f"{msg}: {value!r}")
            raise ValueError(f"{msg}。") from None
        return super().validate(converted)


class CNumber[OutT: float | int](CNumerical[OutT]):
    """
    [非推奨]CNumberは非推奨です。将来のバージョンで削除されます。
    代わりにCNumericalを使用してください。
    """

    def __init__(
        self,
        target_type: type[OutT],
        min_val: OutT | None = None,
        max_val: OutT | None = None,
        *,
        type_strict: bool = False,
    ) -> None:
        msg = "CNumberは非推奨です。代わりにCNumericalを使用してください。"
        warnings.warn(msg, DeprecationWarning, stacklevel=2)
        super().__init__(target_type, min_val, max_val, type_strict=type_strict)


class CInt(CNumerical[int]):
    """
    値を整数に変換し、範囲を検証するコンバータ。
    """

    def __init__(
        self,
        min_val: int | None = None,
        max_val: int | None = None,
    ) -> None:
        super().__init__(target_type=int, min_val=min_val, max_val=max_val)


class CFloat(CNumerical[float]):
    """
    値を浮動小数点数に変換し、範囲を検証するコンバータ。
    """

    def __init__(
        self,
        min_val: float | None = None,
        max_val: float | None = None,
    ) -> None:
        super().__init__(target_type=float, min_val=min_val, max_val=max_val)


class CPath(VPath, Converter[str | Path, Path]):
    """文字列をPathオブジェクトに変換し、属性を検証するコンバータ。"""

    def __init__(
        self,
        *extensions: str,
        must_exist: bool = False,
        path_type: Callable[[Path], bool] | Literal["dir", "file"] | None = None,
    ) -> None:
        super().__init__(*extensions, must_exist=must_exist, path_type=path_type)

    @override
    def validate(self, value: Any) -> Path:
        """Pathオブジェクトに変換してから、VPathの検証を実行する。"""
        try:
            converted = Path(value)
        except (TypeError, ValueError):
            msg = f"`{self.public_name}`を`pathlib.Path`オブジェクトに変換できませんでした"
            logger.exception(f"{msg}: {value!r}")
            raise TypeError(f"{msg}。") from None
        return super().validate(converted)


class CString(VString, Converter[Any, str]):
    """VStringの拡張バリデータ。

    str型に変換可能なオブジェクトは例外を投げずに変換を行います。
    """

    def validate(self, value: Any) -> str:
        tmp_value = value
        if type(tmp_value) is not str:
            try:
                tmp_value = str(tmp_value)
            except Exception:
                msg = f"`{self.public_name}`は`str型`に変換可能な値である必要があります"
                logger.exception(f"{msg}: {tmp_value!r}")
                raise TypeError(f"{msg}。") from None
        return super().validate(tmp_value)


class CTimedelta(VTimedelta, Converter[Any, timedelta]):
    """VTimedeltaの拡張バリデータです。

    timedelta型に変換可能なオブジェクトは例外を投げずに変換を行います。
    """

    cmp_timedelta = re.compile(r"(?:(\d+) days?,? )?(\d+):(\d+):(\d+)(?:\.(\d+))?")

    def validate(self, value: Any) -> timedelta:
        f = None
        if (tv := type(value)) is dict:
            f = self.__try_convert_dict
        elif tv in (list, tuple):
            f = self.__try_convert_container
        elif tv is str:
            f = self.__try_convert_str
        tmp_value = value
        try:
            if f is not None:
                tmp_value = f(tmp_value)
        except Exception:
            msg = f"`{self.public_name}`は`timedelta型`に変換可能な値である必要があります"
            logger.exception(f"{msg}: {tmp_value!r}")
            raise TypeError(f"{msg}") from None
        return super().validate(tmp_value)

    def __try_convert_container(self, value: list | tuple) -> timedelta:
        return timedelta(*value)

    def __try_convert_dict(self, value: dict) -> timedelta:
        return timedelta(**value)

    def __try_convert_str(self, value: str) -> timedelta:
        if (match := self.cmp_timedelta.fullmatch(value)) is not None:
            keys = ("days", "hours", "minutes", "seconds", "microseconds")
            d = {}
            for k, v in zip(keys, match.groups(), strict=True):
                if v is None:
                    continue
                if k == "microseconds":
                    v = v.ljust(6, "0")[:6]
                v = int(v)
                d[k] = v
            return self.__try_convert_dict(d)
        msg = "timedelta型に変換できませんでした"
        logger.error(f"{msg}: `{value!r}`")
        raise ValueError(f"{msg}。")
