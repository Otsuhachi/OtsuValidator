__all__ = (
    "VAny",
    "VBool",
    "VChoice",
    "VDict",
    "VFloat",
    "VInt",
    "VList",
    "VNone",
    "VNumber",
    "VPath",
    "VRange",
    "VRegex",
    "VSequence",
    "VString",
    "VTimedelta",
    "VTuple",
    "VType",
    "_ensure_validator",
)


import re
import warnings
from collections.abc import Callable, Container, Hashable, Iterable
from datetime import timedelta
from pathlib import Path
from typing import Any, Literal, override

from .bases import Validator, VContainer
from .types import FLOAT_INT, Comparable


class VNumber[OutT: FLOAT_INT](Validator[OutT]):
    """数値の範囲を検証するバリデータ。"""

    def __init__(
        self,
        min_val: OutT | None = None,
        max_val: OutT | None = None,
        *,
        type_strict: bool = False,
    ) -> None:
        super().__init__()
        self.min_val = min_val
        self.max_val = max_val
        self.type_strict = type_strict

    def _check_type(self, value: Any) -> None:
        """標準的な数値チェック（サブクラスでオーバーライドされることを想定）。"""
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError(f"'{self.public_name}'は数値(boolを除く)である必要があります。")

    @override
    def validate(self, value: Any) -> OutT:
        self._check_type(value)
        pn = self.public_name
        if (mv := self.min_val) is not None and value < mv:
            msg = f"'{pn}'は{mv}以上である必要があります。"
            raise ValueError(msg)
        if (mv := self.max_val) is not None and value > mv:
            msg = f"'{pn}'は{mv}以下である必要があります。"
            raise ValueError(msg)
        return value


class VSequence[OutT](VContainer[OutT]):
    """VList と VTuple の共通基盤。"""

    def __init__(
        self,
        item_schema: Any,
        *,
        min_len: int | None = None,
        max_len: int | None = None,
        monitoring_overwrite: bool = False,
    ) -> None:
        # スキーマがリストやタプル(集合)か、単一の定義かを判定
        self.is_zip_mode = isinstance(item_schema, (list, tuple))
        if self.is_zip_mode:
            # 個別適用モード: zip(value, schema)で検証
            schema = tuple(_ensure_validator(s) for s in item_schema)
        else:
            # 一律適用モード: 全ての要素に同じバリデータを適用
            schema = _ensure_validator(item_schema)
        super().__init__(schema=schema, monitoring_overwrite=monitoring_overwrite)
        self.min_len = min_len
        self.max_len = max_len

    def _validate_items(self, value: Iterable[Any]) -> list[Any]:
        """中身のバリデーションを実行する。"""
        # 要素数の判定
        value = list(value)
        length = len(value)
        pn = self.public_name
        if (ml := self.min_len) is not None and length < ml:
            msg = f"'{pn}'の要素数は{ml}以上である必要があります。"
            raise ValueError(msg)
        if (ml := self.max_len) is not None and length > ml:
            msg = f"'{pn}'の要素数は{ml}以下である必要があります。"
            raise ValueError(msg)
        if self.is_zip_mode:
            # 個別適用
            validators: tuple[Validator[Any], ...] = self.schema
            if len(validators) != length:
                msg = f"'{pn}'の要素数（{length}）が定義されたスキーマの数（{len(validators)}）と一致しません。"
                raise ValueError(msg)
            return [v.validate(x) for v, x in zip(validators, value, strict=False)]
        else:
            # 一律適用
            validator: Validator[Any] = self.schema
            return [validator.validate(item) for item in value]


class VAny(Validator[Any]):
    """全ての値を許容するバリデータ。"""

    @override
    def validate(self, value: Any) -> Any:
        return value


class VBool(Validator[bool]):
    """真偽値であることを検証するバリデータ。"""

    @override
    def validate(self, value: Any) -> bool:
        if (tv := type(value)) is not bool:
            msg = f"'{self.public_name}'はboolean型である必要があります（指定された型: {tv.__name__}）。"
            raise TypeError(msg)
        return value


class VChoice[OutT](Validator[OutT]):
    """特定の値の選択肢に含まれているかを検証するバリデータ。"""

    def __init__(self, choices: Iterable[OutT]) -> None:
        super().__init__()
        try:
            self.choices: Container[OutT] = set(choices)
        except TypeError:
            self.choices = tuple(choices)

    @override
    def validate(self, value: Any) -> OutT:
        choices = self.choices
        if value not in choices:
            msg = f"'{self.public_name}'は{choices}のいずれかである必要があります。"
            raise ValueError(msg)
        return value


class VDict[InT, OutT](VContainer[dict[InT, OutT]]):
    """
    辞書の構造を検証するバリデータ。
    スキーマに基づき、キーごとの検証を行う。
    """

    def __init__(
        self,
        schema: dict[Hashable, Any],
        *,
        allow_missing: bool = False,  # キーが足りなくてもOKか
        allow_extra: bool = False,  # 未知のキーがあってもOKか
        monitoring_overwrite: bool = False,
    ) -> None:
        normalized_schema = {k: _ensure_validator(v) for k, v in schema.items()}
        super().__init__(
            schema=normalized_schema,
            monitoring_overwrite=monitoring_overwrite,
        )
        self.allow_missing = allow_missing
        self.allow_extra = allow_extra

    @override
    def validate(self, value: Any) -> dict[InT, OutT]:
        pn = self.public_name
        if not isinstance(value, dict):
            msg = f"'{pn}'はdict型である必要があります（指定された型: {type(value).__name__}）。"
            raise TypeError(msg)
        validated_dict: dict[InT, OutT] = {}
        schema: dict[InT, Validator[OutT]] = self.schema

        # 1. スキーマに定義されているキーの検証
        for k, v in schema.items():
            if k in value:
                v.set_name(f"{pn}[{k!r}]")
                validated_dict[k] = v.validate(value[k])
            elif not self.allow_missing:
                msg = f"'{pn}'に必須キー{k!r}が存在しません。"
                raise KeyError(msg)

        # 2. スキーマにない未知のキーハンドリング
        if self.allow_extra:
            for k, v in value.items():
                if k not in schema:
                    validated_dict[k] = v
        elif any(k not in schema for k in value):
            # 許可されていないキーがある場合、見つけたものを通知
            extra_keys = [k for k in value if k not in schema]
            msg = f"'{pn}'に未許可のキーが含まれています: {extra_keys}。"
            raise KeyError(msg)
        return validated_dict


class VFloat(VNumber[float]):
    """浮動小数点数専用のバリデータ。"""

    def __init__(
        self,
        min_val: float | None = None,
        max_val: float | None = None,
    ) -> None:
        super().__init__(min_val, max_val, type_strict=True)

    @override
    def _check_type(self, value: Any) -> None:
        if not isinstance(value, float):
            msg = f"'{self.public_name}'はfloat型である必要があります。"
            raise TypeError(msg)


class VInt(VNumber[int]):
    """整数専用のバリデータ。"""

    def __init__(
        self,
        min_val: int | None = None,
        max_val: int | None = None,
    ) -> None:
        super().__init__(min_val, max_val, type_strict=True)

    @override
    def _check_type(self, value: Any) -> None:
        if not isinstance(value, int) or isinstance(value, bool):
            msg = f"'{self.public_name}'はint型(boolを除く)である必要があります。"
            raise TypeError(msg)


class VList[OutT](VSequence[list[Any]]):
    @override
    def validate(self, value: Any) -> list[OutT]:
        if not isinstance(value, list):
            msg = f"'{self.public_name}'はlist型である必要があります。"
            raise TypeError(msg)
        return self._validate_items(value)


class VNone(Validator[None]):
    """値がNoneであることを検証するバリデータ。"""

    @override
    def validate(self, value: Any) -> None:
        if value is not None:
            msg = f"'{self.public_name}'はNoneである必要があります（指定された型: {type(value).__name__}）。"
            raise TypeError(msg)
        return None


class VPath(Validator[Path]):
    """
    pathlib.Path オブジェクトの属性を検証するバリデータ。
    """

    def __init__(
        self,
        *extensions: str,
        must_exist: bool = False,
        path_type: Literal["dir", "file"] | Callable[[Path], bool] | None = None,
    ) -> None:
        super().__init__()
        self.extensions = tuple(ext if ext.startswith(".") else f".{ext}" for ext in extensions)
        self.must_exist = must_exist

        # path_typeの解決
        if path_type == "file":
            self.check_func = Path.is_file
        elif path_type == "dir":
            self.check_func = Path.is_dir
        else:
            self.check_func = path_type

    @override
    def validate(self, value: Any) -> Path:
        pn = self.public_name
        if not isinstance(value, Path):
            msg = f"'{pn}'はpathlib.Path型である必要があります（指定された型: {type(value).__name__}）。"
            raise TypeError(msg)
        exists = value.exists()

        # 1. 存在チェック
        if self.must_exist and not exists:
            msg = f"'{pn}'のパスが存在しません: {value}。"
            raise FileNotFoundError(msg)
        # 2. 種類チェック
        cf = self.check_func
        if cf and exists:
            if not cf(value):
                func_name = getattr(cf, "__name__", "custom check")
                msg = f"'{pn}'はパス種別検証に失敗しました: {func_name}({value})。"
                raise ValueError(msg)

        # 3. 拡張子チェック
        exts = self.extensions
        if exts and value.suffix not in exts:
            match len(exts):
                case 0:
                    msg = f"'{pn}'に拡張子が指定されていません。"
                    raise ValueError(msg)
                case 1:
                    txt_exts = exts[0]
                case _:
                    txt_exts = "[" + ", ".join(exts) + "]"
            msg = f"'{pn}'の拡張子は{txt_exts}のいずれかである必要があります（指定された拡張子: {value.suffix!r}）。"
            raise ValueError(msg)
        return value


class VRange[OutT: Comparable](Validator[OutT]):
    """比較可能なオブジェクトの範囲を検証するバリデータ。"""

    def __init__(
        self,
        min_val: OutT | None = None,
        max_val: OutT | None = None,
    ) -> None:
        super().__init__()
        self.min_val = min_val
        self.max_val = max_val

    @override
    def validate(self, value: Any) -> OutT:
        # value が比較可能であることを前提とする
        # 厳密な型チェックが必要な場合は VType と組み合わせて使用する
        pn = self.public_name
        try:
            if (mv := self.min_val) is not None and value < mv:
                msg = f"'{pn}'は{mv}以上である必要があります。"
                raise ValueError(msg)
            if (mv := self.max_val) is not None and value > mv:
                msg = f"'{pn}'は{mv}以下である必要があります。"
                raise ValueError(msg)
        except TypeError:
            msg = f"'{pn}'（型: {type(value).__name__}）は比較可能ではありません。"
            raise TypeError(msg) from None
        return value


class VString(Validator[str]):
    """文字列の長さを検証するバリデータ。"""

    def __init__(
        self,
        min_len: int | None = None,
        max_len: int | None = None,
        pattern: str | re.Pattern[str] | None = None,
        *,
        checker: Callable[[str], bool] | None = None,
    ) -> None:
        super().__init__()
        self.min_len = min_len
        self.max_len = max_len
        self.pattern = re.compile(pattern) if isinstance(pattern, str) else pattern
        self.checker = checker

    @override
    def validate(self, value: Any) -> str:
        pn = self.public_name
        # 1. 型チェック
        if not isinstance(value, str):
            msg = f"'{pn}'はstr型である必要があります。"
            raise TypeError(msg)
        # 2. 長さチェック
        length = len(value)
        if (ml := self.min_len) is not None and length < ml:
            msg = f"'{pn}'の長さは{ml}以上である必要があります。"
            raise ValueError(msg)
        if (ml := self.max_len) is not None and length > ml:
            msg = f"'{pn}'の長さは{ml}以下である必要があります。"
            raise ValueError(msg)
        # 3. 正規表現チェック
        if (pattern := self.pattern) and not pattern.search(value):
            msg = f"'{pn}'はパターン'{pattern.pattern}'にマッチしません。"
            raise ValueError(msg)
        # 4. カスタムチェッカー
        if (checker := self.checker) and not checker(value):
            msg = f"'{pn}'はカスタム検証に失敗しました。"
            raise ValueError(msg)
        return value


class VRegex(VString):
    """
    [非推奨]VRegexは非推奨です。将来のバージョンで削除されます。
    代わりにVString(pattern=...)を使用してください。
    """

    def __init__(
        self,
        pattern: str,
        min_len: int | None = None,
        max_len: int | None = None,
        checker: Callable[[str], bool] | None = None,
    ) -> None:
        msg = "VRegexは非推奨です。代わりにVString(pattern=...)を使用してください。"
        warnings.warn(msg, DeprecationWarning, stacklevel=2)
        super().__init__(min_len, max_len, pattern, checker=checker)


class VTimedelta(Validator[timedelta]):
    """timedelta オブジェクトであることを検証するバリデータ。"""

    @override
    def validate(self, value: Any) -> timedelta:
        if not isinstance(value, timedelta):
            msg = f"'{self.public_name}'はtimedelta型である必要があります（指定された型: {type(value).__name__}）。"
            raise TypeError(msg)
        return value


class VTuple[OutT](VSequence[tuple[OutT, ...]]):
    @override
    def validate(self, value: Any) -> tuple[OutT, ...]:
        if not isinstance(value, tuple):
            msg = f"'{self.public_name}'はtuple型である必要があります。"
            raise TypeError(msg)
        return tuple(self._validate_items(value))


class VType[OutT](Validator[OutT]):
    """指定された型であることを検証するバリデータ。"""

    def __init__(self, target_type: type[OutT], strict: bool = True) -> None:
        super().__init__()
        self.target_type = target_type
        self.strict = strict

    @override
    def validate(self, value: Any) -> OutT:
        t_type = self.target_type
        if self.strict:
            is_valid = type(value) is t_type
            type_name = t_type.__name__
        else:
            is_valid = isinstance(value, t_type)
            type_name = f"{t_type.__name__}のサブクラス"
        if not is_valid:
            msg = f"'{self.public_name}'は{type_name}である必要があります（指定された型: {type(value).__name__}）。"
            raise TypeError(msg)
        return value


def _ensure_validator(arg: Any) -> Validator[Any]:
    """
    入力を適切なバリデータに変換する。
    1. Validator インスタンスならそのまま返す。
    2. 型 (type) なら VType(strict=True) に変換。
    3. インスタンス (str, int 等) なら対応するバリデータ、
       または VType(type(arg), strict=False) にフォールバック。
    """
    if isinstance(arg, Validator):
        return arg
    # 1. 型が直接渡された場合: type(value) is Tの厳密判定
    if isinstance(arg, type):
        return VType(arg, strict=True)

    # 2. 値(インスタンス)が渡された場合: isinstance(value, T)の継承許容判定
    if isinstance(arg, bool):
        return VBool()
    if isinstance(arg, int):
        return VInt()
    if isinstance(arg, float):
        return VFloat()
    if isinstance(arg, str):
        return VString()
    if isinstance(arg, Path):
        return VPath()
    if isinstance(arg, timedelta):
        return VTimedelta()

    if isinstance(arg, list):
        return VList(arg)
    if isinstance(arg, tuple):
        return VTuple(arg)
    if isinstance(arg, dict):
        return VDict(arg)

    # 未対応の型/インスタンスに対するフォールバック
    # インスタンスが渡されたので、その型に対して strict=False で登録
    return VType(type(arg), strict=False)
