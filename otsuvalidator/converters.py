import re

from datetime import timedelta
from pathlib import Path
from typing import Any, Callable, Optional, Tuple, Union, cast, overload

from .bases import CNumerical, Converter
from .validators import (VBool, VFloat, VInt, VNumber, VPath, VString, VTimedelta)


class CBool(VBool, Converter):
    """VBoolの拡張バリデータです。
    
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
    def __init__(self,
                 true_data: Optional[Tuple[Any, ...]] = None,
                 false_data: Optional[Tuple[Any, ...]] = None,
                 checker: Optional[Tuple[Callable[[Any], bool], ...]] = None):
        """ユーザ定義のTrueにしたい値、Falseにしたい値を設定してバリデータを生成します。

        Args:
            true_data (Optional[Tuple[Any, ...]], optional): Trueにしたい値です。
            false_data (Optional[Tuple[Any, ...]], optional): Falseにしたい値です。
            checker (Optional[Tuple[Callable[[Any], bool], ...]], optional): 真偽判定用の関数です。
        """
        self.true_data = true_data
        self.false_data = false_data
        self.checker = checker

    def validate(self, value) -> bool:
        E = self.ERRMSG
        # ユーザ定義で真偽を確認
        if self.true_data is not None and value in self.true_data:
            value = True
        if self.false_data is not None and value in self.false_data:
            value = False
        if self.checker is not None:
            for checker in self.checker:
                try:
                    tmp = checker(value)
                    if tmp is None:
                        continue
                    value = tmp
                except:
                    continue
        # クラス定義で真偽を確認
        if (tv := type(value)) is str:
            value = cast(str, value)
            value = value.lower()
            if value in (yes := ('true', 'yes', 'y', '1')):
                value = True
            elif value in (no := ('false', 'no', 'n', '0')):
                value = False
            else:
                msg = E(f'{yes}または{no}のいずれかである必要があります', value)
                raise ValueError(msg)
        elif tv is int:
            if value == 1:
                value = True
            elif value == 0:
                value = False
            else:
                msg = E('1または0である必要があります', value)
                raise ValueError(msg)
        elif tv is float:
            if value == 1.0:
                value = True
            elif value == 0.0:
                value = False
            else:
                msg = E('1.0または0.0である必要があります', value)
                raise ValueError(msg)
        elif tv is bool:
            pass
        else:
            msg = E('Yes/Noとして解釈できる必要があります', value)
            raise TypeError(msg)
        return super().validate(value)

    def super_validate(self, value: Any) -> bool:
        return super().validate(value)


class CNumber(VNumber, CNumerical):
    """VNumberの拡張バリデータです。

    (int, float)型に変換可能なオブジェクトは例外を投げずに変換を試みます。
    どちらにも変換可能な場合、int(value)==float(value)の結果が同じ時はintそれ以外はfloatで変換されます。
    """
    @overload
    def validate(self, value: int) -> int:
        ...

    @overload
    def validate(self, value: float) -> float:
        ...

    def validate(self, value: Any) -> Union[int, float]:
        E = self.ERRMSG
        value = value
        if type(value) not in (int, float):
            i = self.try_int(value)
            f = self.try_float(value)
            if i is None and f is None:
                msg = E('数値として扱える必要があります', value)
                raise TypeError(msg)
            if i is not None and f is not None:
                value = i if i == f else f
            elif i:
                value = i
            else:
                value = f
        return super().validate(value)

    @overload
    def super_validate(self, value: int) -> int:
        ...

    @overload
    def super_validate(self, value: float) -> float:
        ...

    def super_validate(self, value: Any) -> Union[int, float]:
        return super().validate(value)


class CFloat(VFloat, CNumerical):
    """VFloatの拡張バリデータです。

    float型に変換可能なオブジェクトは例外を投げずに変換を試みます。
    """
    def validate(self, value: Any) -> float:
        if type(value) is not float:
            convalue = self.try_float(value)
            if convalue is None:
                msg = self.ERRMSG('float型として扱える必要があります', value)
                raise TypeError(msg)
            value = convalue
        return super().validate(value)

    def super_validate(self, value: Any) -> float:
        return super().validate(value)


class CInt(VInt, CNumerical):
    """VIntの拡張バリデータです。

    int型に変換可能なオブジェクトは例外を投げずに変換を試みます。
    """
    def validate(self, value) -> int:
        if type(value) is not int:
            convalue = self.try_int(value)
            if convalue is None:
                msg = self.ERRMSG('int型として扱える必要があります', value)
                raise TypeError(msg)
            value = convalue
        return super().validate(value)

    def super_validate(self, value: Any) -> int:
        return super().validate(value)


class CPath(VPath, Converter):
    """VPathの拡張バリデータです。

    Path型に変換可能なオブジェクトは例外を投げずに変換を行います。
    """
    def validate(self, value: Any) -> Path:
        if not isinstance(value, Path):
            try:
                value = Path(value)
            except:
                msg = self.ERRMSG('Path型として扱える必要があります', value)
                raise TypeError(msg)
        return super().validate(value)

    def super_validate(self, value: Any) -> Path:
        return super().validate(value)


class CString(VString, Converter):
    """VStringの拡張バリデータです。

    str型に変換可能なオブジェクトは例外を投げずに変換を行います。
    """
    def validate(self, value: Any) -> str:
        if type(value) is not str:
            try:
                value = str(value)
            except:
                msg = self.ERRMSG('str型として扱える必要があります', value)
                raise TypeError(msg)
        return super().validate(value)

    def super_validate(self, value: Any) -> str:
        return super().validate(value)


class CTimedelta(VTimedelta, Converter):
    """VTimedeltaの拡張バリデータです。

    timedelta型に変換可能なオブジェクトは例外を投げずに変換を行います。
    """
    cmp_timedelta = re.compile('(\\d+ ?days?,? ?)?(\\d+):(\\d+):(\\d+)(\\.\\d+)?')
    cmp_days = re.compile('(\\d+) ?days?,? ?')

    def validate(self, value: Any) -> timedelta:
        f = None
        if (tv := type(value)) is dict:
            f = self.__try_convert_dict
        elif tv in (list, tuple):
            f = self.__try_convert_container
        elif tv is str:
            f = self.__try_convert_str
        try:
            if f is not None:
                value = f(value)
        except:
            msg = self.ERRMSG('timedelta型として扱える必要があります', value)
            raise TypeError(msg)
        return super().validate(value)

    def super_validate(self, value: Any) -> Any:
        return super().validate(value)

    def __try_convert_dict(self, value: dict) -> timedelta:
        return timedelta(**value)

    def __try_convert_container(self, value: Union[list, tuple]) -> timedelta:
        return timedelta(*value)

    def __try_convert_str(self, value: str) -> timedelta:
        if (match := self.cmp_timedelta.match(value)) is not None:
            keys = ('days', 'hours', 'minutes', 'seconds', 'microseconds')
            d = {}
            for k, v in zip(keys, match.groups()):
                if v is None:
                    continue
                if k == 'days':
                    if (find := self.cmp_days.match(v)) is not None:
                        v = find.groups()[0]
                elif k == 'microseconds':
                    v = v[1:]
                v = int(v)
                d[k] = v
            return self.__try_convert_dict(d)
        raise TypeError
