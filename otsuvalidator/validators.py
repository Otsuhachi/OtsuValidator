import inspect
import re

from datetime import timedelta
from pathlib import Path
from typing import Any, Callable, Optional, Union, cast, overload

from otsuvalidator.bases import Converter, Validator, VContainer


class VBool(Validator):
    """真偽値かどうかを確認するバリデータです。
    """
    def validate(self, value: Any) -> bool:
        if type(value) is not bool:
            msg = self.ERRMSG('bool型である必要があります', value)
            raise TypeError(msg)
        return value


class VChoice(Validator):
    """選択肢の中から1つが選択されているかどうかを確認するバリデータです。
    """
    def __init__(self, *options: Any):
        """選択肢を設定し、バリデータを生成します。
        """
        if not options:
            msg = self.ERRMSG('1つ以上のoptionsを設定してください', options, False)
            raise ValueError(msg)
        self.options = set(options)

    def validate(self, value: Any) -> Any:
        if value not in self.options:
            msg = self.ERRMSG(f'{self.options}のいずれかである必要があります', value)
            raise ValueError(msg)
        return value


class VNumber(Validator):
    """適切な数値かどうかを確認するバリデータです。
    """
    def __init__(self, minimum: Optional[Union[int, float]] = None, maximum: Optional[Union[int, float]] = None):
        """下限値と上限値を指定してバリデータを生成します。

        Args:
            minimum (Optional[Union[int, float]], optional): 下限値です。
            maximum (Optional[Union[int, float]], optional): 上限値です。
        """
        self.minimum = minimum
        self.maximum = maximum

    @overload
    def validate(self, value: int) -> int:
        ...

    @overload
    def validate(self, value: float) -> float:
        ...

    def validate(self, value: Any) -> Any:
        E = self.ERRMSG
        if type(value) not in (int, float):
            msg = E('(int, float)型のいずれかである必要があります', value)
            raise TypeError(msg)
        if (mini := self.minimum) is not None and value < mini:
            msg = E(f'{mini}より小さい値を設定することはできません', value)
            raise ValueError(msg)
        if (maxi := self.maximum) is not None and value > maxi:
            msg = E(f'{maxi}より大きい値を設定することはできません', value)
            raise ValueError(msg)
        return value


class VFloat(VNumber):
    """適切な浮動小数点数かどうかを確認するバリデータです。
    """
    def validate(self, value: Any) -> float:
        if type(value) is not float:
            msg = self.ERRMSG('float型である必要があります', value)
            raise TypeError(msg)
        return super().validate(value)


class VInt(VNumber):
    """適切な整数かどうかを確認するバリデータです。
    """
    def validate(self, value: Any) -> int:
        if type(value) is not int:
            msg = self.ERRMSG('int型である必要があります', value)
            raise TypeError(msg)
        return super().validate(value)


class VPath(Validator):
    """適切なパスかどうかを確認するバリデータです。
    """
    def __init__(self, *suffix: str, exist_only: bool = False):
        """許可する拡張子とパスの存在確認を行うかを設定し、バリデータを生成します。

        拡張子は複数許可することもできます。
        また、先頭の'.'はあってもなくても等価です。
        '.txt' == 'txt'

        Args:
            exist_only (bool, optional): 有効にすると、存在しないパスに対して例外を投げます。
        """
        self.exist_only = exist_only
        self.suffix = tuple(set(map(lambda x: '.' + x.lstrip('.') if x else x, suffix)))

    def validate(self, value: Any) -> Path:
        E = self.ERRMSG
        if not isinstance(value, Path):
            msg = E('Path型である必要があります', value)
            raise TypeError(msg)
        if (sf := self.suffix):
            if value.suffix not in sf:
                msg = E(f'拡張子が{sf[0]}である必要があります' if len(sf) == 1 else f'拡張子が{sf}のいずれかである必要があります', value)
                raise ValueError(msg)
        if self.exist_only and not value.exists():
            msg = E('存在するパスである必要があります', value)
            raise FileNotFoundError(msg)
        return value


class VString(Validator):
    """適切な文字列かどうかを確認するバリデータです。
    """
    def __init__(self, minimum: Optional[int] = None, maximum: Optional[int] = None, checker: Optional[Callable[[str], bool]] = None):
        """最低文字数、最大文字数、確認関数を設定してバリデータを生成します。

        Args:
            minimum (Optional[int], optional): 最低文字数です。
            maximum (Optional[int], optional): 最大文字数です。
            checker (Optional[Callable[[str],bool]], optional): 指定した形式であるかを返す関数です。
        """
        self.minimum = minimum
        self.maximum = maximum
        self.checker = checker

    def validate(self, value: Any) -> str:
        E = self.ERRMSG
        if type(value) is not str:
            msg = E('str型である必要があります', value)
            raise TypeError(msg)
        lv = len(value)
        if (mini := self.minimum) is not None and lv < mini:
            msg = E(f'{mini}文字以上である必要があります', value)
            raise ValueError(msg)
        if (maxi := self.maximum) is not None and lv > maxi:
            msg = E(f'{maxi}文字以下である必要があります', value)
            raise ValueError(msg)
        if (checker := self.checker) is not None and not checker(value):
            msg = E(f'指定した形式に対応している必要があります。{repr(checker)}', value)
            raise ValueError(msg)
        return value


class VRegex(VString):
    """VStringの拡張バリデータです。

    VStringの条件に加え、正規表現によるチェックをしたい場合に使用できます。
    """
    pattern = VString()

    def __init__(self, pattern: str, minimum: Optional[int] = None, maximum: Optional[int] = None, checker: Optional[Callable[[str], bool]] = None):
        """正規表現、最低文字数、最大文字数、確認関数を設定してバリデータを生成します。

        Args:
            pattern (str): 正規表現です。
            minimum (Optional[int], optional): 最低文字数です。
            maximum (Optional[int], optional): 最大文字数です。
            checker (Optional[Callable[[str],bool]], optional): 指定した形式であるかを返す関数です。
        """
        super().__init__(minimum=minimum, maximum=maximum, checker=checker)
        self.pattern = pattern

    def validate(self, value: Any) -> str:
        value = super().validate(value)
        if not re.match(self.pattern, value):
            msg = self.ERRMSG(f'正規表現{repr(self.pattern)}に対応している必要があります', value)
            raise ValueError(msg)
        return value


class VTimedelta(Validator):
    """適切な経過時間かどうかを確認するバリデータです。
    """
    def validate(self, value: Any) -> timedelta:
        if type(value) is not timedelta:
            msg = self.ERRMSG(f'timedelta型である必要があります', value)
            raise TypeError(msg)
        return value


class VDict(VContainer):
    """適切な辞書かどうかを確認するバリデータです。
    """
    def __init__(self, TEMPLATE: dict, allow_missing_key: bool, monitoring_overwrite: bool = True, allow_convert: bool = True):
        """雛形、キーの欠落を許可するか、アクセス時に再検証を行うか、変換を許可するかを設定してバリデータを生成します。

        Args:
            TEMPLATE (dict): 雛形です。
            allow_missing_key (bool): キーの欠落を許可するかどうかです。
            monitoring_overwrite (bool, optional): アクセス時に再検証を行うかどうかです。要素数などによっては時間がかかる場合があります。不変であることが保証されている場合などには無効にしてください。
            allow_convert (bool, optional): コンバータによる要素の変換を許可するかどうかです。
        """
        super().__init__(TEMPLATE, monitoring_overwrite=monitoring_overwrite, allow_convert=allow_convert)
        self.allow_missing_key = allow_missing_key

    def validate(self, value) -> dict:
        E = self.ERRMSG
        if not isinstance(value, dict):
            msg = E('dict型である必要があります', value)
            raise TypeError(msg)
        self.TEMPLATE = cast(dict, self.TEMPLATE)
        KEYS = set(self.TEMPLATE.keys())
        VKEYS = set(value.keys())
        if (KEYS ^ VKEYS):
            if (unnecessary_keys := VKEYS - KEYS):
                msg = E(f'以下のキーを設定することはできません。({unnecessary_keys})', value)
                raise ValueError(msg)
            if not self.allow_missing_key and (missing_key := KEYS - VKEYS):
                msg = E(f'以下のキーを設定する必要があります。({missing_key})', value)
                raise ValueError(msg)
        for k, v in value.items():
            tv = self.TEMPLATE.get(k)
            if isinstance(tv, Validator):
                try:
                    if isinstance(tv, Converter):
                        if self.allow_convert:
                            value[k] = tv.validate(v)
                        else:
                            tv.super_validate(v)
                    else:
                        tv.validate(v)
                except Exception as e:
                    etype = type(e)
                    msg = E(f'キー{repr(k)}は不正な値です', v, False)
                    raise etype(msg)
        return value


class VList(VContainer):
    """適切なリストか確認するバリデータです。
    """
    def __init__(self,
                 TEMPLATE: Union[list, Validator, Any],
                 minimum: Optional[int] = None,
                 maximum: Optional[int] = None,
                 monitoring_overwrite: bool = True,
                 allow_convert: bool = True):
        """雛形、最小、最大要素数、アクセス時に再検証を行うか、変換を許可するかを設定し、バリデータを作成します。

        TEMPLATEがAnyの場合、クラスか、インスタンスかでbool以外の型チェックの挙動が変化します。
        クラスの場合にはtype(TEMPLATE) is type(v)、インスタンスの場合にはisinstance(v, type(TEMPLATE))で判定が行われます。
        これはTEMPLATEがlistでValidator以外を含めた時にも適応されます。

        Args:
            TEMPLATE (Union[list, Validator, Any]): 雛形です。渡す型によって挙動が変化します。
            minimum (Optional[int], optional): 最小要素数です。TEMPLATEがリストの場合には機能しません。
            maximum (Optional[int], optional): 最大要素数です。TEMPLATEがリストの場合には機能しません。
            monitoring_overwrite (bool, optional): アクセス時に再検証を行うかどうかです。要素数などによっては時間がかかる場合があります。不変であることが保証されている場合などには無効にしてください。
            allow_convert (bool, optional): コンバータによる要素の変換を許可するかどうかです。
        """
        super().__init__(TEMPLATE, monitoring_overwrite=monitoring_overwrite, allow_convert=allow_convert)
        self.minimum = minimum
        self.maximum = maximum

    def validate(self, value: Any) -> list:
        E = self.ERRMSG
        if type(value) is not list:
            msg = E('list型である必要があります', value)
            raise TypeError(msg)
        if type(self.TEMPLATE) is list:
            return self._validate_of_structure(value)
        lv = len(value)
        if (mini := self.minimum) is not None and lv < mini:
            msg = E(f'あと{mini-lv}個設定する必要があります', value)
            raise ValueError(msg)
        if (maxi := self.maximum) is not None and lv > maxi:
            msg = E(f'あと{lv-maxi}個減らす必要があります', value)
            raise ValueError(msg)
        if isinstance(self.TEMPLATE, Validator):
            return self._validate_by_validator(value)
        else:
            return self._validate_by_type(value)

    def _validate_by_type(self, value) -> list:
        E = self.ERRMSG
        vtype = self.TEMPLATE if (is_type := inspect.isclass(self.TEMPLATE)) else type(self.TEMPLATE)
        for i, v in enumerate(value):
            msg = E(f'インデックス{i}は{vtype.__name__}型である必要があります', v, False)
            if type(v) is bool:
                if vtype is not bool:
                    raise TypeError(msg)
            elif is_type:
                if type(v) is not vtype:
                    raise TypeError(msg)
            else:
                if not isinstance(v, vtype):
                    msg = E(f'インデックス{i}は{vtype.__name__}型あるいはそのサブクラスである必要があります', v, False)
                    raise TypeError(msg)
        return value

    def _validate_by_validator(self, value) -> list:
        T = cast(Union[Validator, Converter], self.TEMPLATE)
        for i, v in enumerate(value):
            try:
                if isinstance(T, Converter):
                    if self.allow_convert:
                        value[i] = T.validate(v)
                    else:
                        T.super_validate(v)
                else:
                    T.validate(v)
            except Exception as e:
                etype = type(e)
                msg = self.ERRMSG(f'インデックス{i}は不正な値です', v, False)
                raise etype(msg)
        return value

    def _validate_of_structure(self, value) -> list:
        E = self.ERRMSG
        if (diff_len := len(value) - len(self.TEMPLATE)) > 0:
            msg = E(f'あと{diff_len}個減らす必要があります', value)
            raise ValueError(msg)
        if diff_len < 0:
            msg = E(f'あと{diff_len*-1}個設定する必要があります', value)
            raise ValueError(msg)
        for i, (v, validator) in enumerate(zip(value, self.TEMPLATE)):
            if isinstance(validator, Validator):
                try:
                    if isinstance(validator, Converter):
                        if self.allow_convert:
                            value[i] = validator.validate(v)
                        else:
                            validator.super_validate(v)
                    else:
                        validator.validate(v)
                except Exception as e:
                    etype = type(e)
                    msg = E(f'インデックス{i}は不正な値です', v, False)
                    raise etype(msg)
            else:
                vtype = validator if (is_type := inspect.isclass(validator)) else type(validator)
                msg = E(f'インデックス{i}は{vtype.__name__}型である必要があります', v, False)
                if type(v) is bool:
                    if vtype is not bool:
                        raise TypeError(msg)
                elif is_type:
                    if type(v) is not vtype:
                        raise TypeError(msg)
                else:
                    if not isinstance(v, vtype):
                        msg = E(f'インデックス{i}は{vtype.__name__}型あるいはそのサブクラスである必要があります', v, False)
                        raise TypeError(msg)
        return value


class VTuple(VContainer):
    """適切なタプルか確認するバリデータです。
    """
    def __init__(self,
                 TEMPLATE: Union[tuple, Validator, Any],
                 minimum: Optional[int] = None,
                 maximum: Optional[int] = None,
                 monitoring_overwrite: bool = True,
                 allow_convert: bool = True):
        """雛形、最小、最大要素数、アクセス時に再検証を行うか、変換を許可するかを設定し、バリデータを作成します。

        TEMPLATEがAnyの場合、クラスオブジェクトか、インスタンスかでbool以外の型チェックの挙動が変化します。
        具体的にはクラスの場合にはtype(TEMPLATE) is type(v)、インスタンスの場合にはisinstance(v, type(TEMPLATE))で判定が行われます。
        これはTEMPLATEがtupleでValidator以外を含めた時にも適応されます。


        Args:
            TEMPLATE (Union[tuple, Validator, Any]): 雛形です。渡す型によって挙動が変化します。
            minimum (Optional[int], optional): 最小要素数です。TEMPLATEがタプルの場合には機能しません。
            maximum (Optional[int], optional): 最大要素数です。TEMPLATEがタプルの場合には機能しません。
            monitoring_overwrite (bool, optional): アクセス時に再検証を行うかどうかです。要素数などによっては時間がかかる場合があります。不変であることが保証されている場合などには無効にしてください。
            allow_convert (bool, optional): コンバータによる要素の変換を許可するかどうかです。
        """
        super().__init__(TEMPLATE, monitoring_overwrite=monitoring_overwrite, allow_convert=allow_convert)
        self.minimum = minimum
        self.maximum = maximum

    def validate(self, value: Any) -> tuple:
        E = self.ERRMSG
        if type(value) is not tuple:
            msg = E('tuple型である必要があります', value)
            raise TypeError(msg)
        if type(self.TEMPLATE) is tuple:
            return self._validate_of_structure(value)
        lv = len(value)
        if (mini := self.minimum) is not None and lv < mini:
            msg = E(f'あと{mini-lv}個設定する必要があります', value)
            raise ValueError(msg)
        if (maxi := self.maximum) is not None and lv > maxi:
            msg = E(f'あと{lv-maxi}個減らす必要があります', value)
            raise ValueError(msg)
        if isinstance(self.TEMPLATE, Validator):
            return self._validate_by_validator(value)
        else:
            return self._validate_by_type(value)

    def _validate_by_type(self, value) -> tuple:
        E = self.ERRMSG
        vtype = self.TEMPLATE if (is_type := inspect.isclass(self.TEMPLATE)) else type(self.TEMPLATE)
        for i, v in enumerate(value):
            msg = E(f'インデックス{i}は{vtype.__name__}型である必要があります', v, False)
            if type(v) is bool:
                if vtype is not bool:
                    raise TypeError(msg)
            elif is_type:
                if type(v) is not vtype:
                    raise TypeError(msg)
            else:
                if not isinstance(v, vtype):
                    msg = E(f'インデックス{i}は{vtype.__name__}型あるいはそのサブクラスである必要があります', v, False)
                    raise TypeError(msg)
        return value

    def _validate_by_validator(self, value) -> tuple:
        if self.allow_convert:
            return self._validate_by_validator_allow(value)
        if isinstance(self.TEMPLATE, Converter):
            validate = self.TEMPLATE.super_validate
        else:
            validate = self.TEMPLATE.validate
        for i, v in enumerate(value):
            try:
                validate(v)
            except Exception as e:
                etype = type(e)
                msg = self.ERRMSG(f'インデックス{i}は不正な値です', v, False)
                raise etype(msg)
        return value

    def _validate_by_validator_allow(self, value) -> tuple:
        self.TEMPLATE = cast(Union[Validator, Converter], self.TEMPLATE)
        res = []
        for i, v in enumerate(value):
            try:
                res.append(self.TEMPLATE.validate(v))
            except Exception as e:
                etype = type(e)
                msg = self.ERRMSG(f'インデックス{i}は不正な値です', v, False)
                raise etype(msg)
        return tuple(res)

    def _validate_of_structure(self, value) -> tuple:
        E = self.ERRMSG
        if (diff_len := len(value) - len(self.TEMPLATE)) > 0:
            msg = E(f'あと{diff_len}個減らす必要があります', value)
            raise ValueError(msg)
        if diff_len < 0:
            msg = E(f'あと{diff_len*-1}個設定する必要があります', value)
            raise ValueError(msg)
        if self.allow_convert:
            return self._validate_of_structure_allow(value)
        for i, (v, validator) in enumerate(zip(value, self.TEMPLATE)):
            if isinstance(validator, Validator):
                try:
                    if isinstance(validator, Converter):
                        validator.super_validate(v)
                    else:
                        validator.validate(v)
                except Exception as e:
                    etype = type(e)
                    msg = E(f'インデックス{i}は不正な値です', v, False)
                    raise etype(msg)
            else:
                vtype = validator if (is_type := inspect.isclass(validator)) else type(validator)
                msg = E(f'インデックス{i}は{vtype.__name__}型である必要があります', v, False)
                if type(v) is bool:
                    if vtype is not bool:
                        raise TypeError(msg)
                elif is_type:
                    if type(v) is not vtype:
                        raise TypeError(msg)
                else:
                    if not isinstance(v, vtype):
                        msg = E(f'インデックス{i}は{vtype.__name__}型あるいはそのサブクラスである必要があります', v, False)
                        raise TypeError(msg)
        return value

    def _validate_of_structure_allow(self, value) -> tuple:
        E = self.ERRMSG
        res = []
        for i, (v, validator) in enumerate(zip(value, self.TEMPLATE)):
            if isinstance(validator, Validator):
                try:
                    if isinstance(validator, Converter):
                        v = validator.validate(v)
                    else:
                        validator.validate(v)
                except Exception as e:
                    etype = type(e)
                    msg = E(f'インデックス{i}は不正な値です', v, False)
                    raise etype(msg)
            else:
                vtype = validator if (is_type := inspect.isclass(validator)) else type(validator)
                msg = E(f'インデックス{i}は{vtype.__name__}型である必要があります', v, False)
                if type(v) is bool:
                    if vtype is not bool:
                        raise TypeError(msg)
                elif is_type:
                    if type(v) is not vtype:
                        raise TypeError(msg)
                else:
                    if not isinstance(v, vtype):
                        msg = E(f'インデックス{i}は{vtype.__name__}型あるいはそのサブクラスである必要があります', v, False)
                        raise TypeError(msg)
            res.append(v)
        return tuple(res)
