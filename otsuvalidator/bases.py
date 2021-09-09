from abc import ABC, abstractmethod
from typing import Any, Optional, Union


class Validator(ABC):
    """すべてのバリデータの基底クラスです。

    このクラスを継承してvalidateメソッドを定義してください。
    
    またvalidateメソッドは検証を通過したvalueを返すようにしてください。
    これはコンバータ等に流用するときのためです。
    """
    def __set_name__(self, cls, name):
        self.name = name
        self.private_name = '_' + name

    def __get__(self, instance, otype):
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        value = self.validate(value)
        setattr(instance, self.private_name, value)

    @abstractmethod
    def validate(self, value: Any) -> Any:
        pass

    def ERRMSG(self, text: str, cause: Any, is_attribute: bool = True) -> str:
        """エラーメッセージを生成します。

        エラーメッセージは以下の形式となります。
        is_attribute=True: '<属性"{name}"は>{text}。({rv}: {type(cause).__name__})'
        is_attribute=False: '{text}。({rv}: {type(cause).__name__})

        rvはrepr(value)ですが、50文字以上になる場合は先頭と末尾の10文字を'...'で挟んだ形式になります。
        <属性{name}は>部分はディスクリプタとして使用されている場合かつ、is_attributeがTrueの時に表示されます。

        Args:
            text (str): 基本のエラーメッセージです。
            cause (Any): 原因となったオブジェクトです。
            is_attribute (bool, optional): 属性で発生したエラーです。

        Returns:
            str: エラーメッセージです。
        """
        text = text.rstrip('。')
        if is_attribute and hasattr(self, 'private_name'):
            text = f'属性{repr(self.name)}は' + text
        rv = repr(cause)
        if len(rv) > 50:
            rv = rv[:10] + '...' + rv[-10:]
        text += f'。({rv}: {type(cause).__name__})'
        return text


class VContainer(Validator):
    """コンテナオブジェクト用バリデータの基底クラスです。

    __set__を経由せずに内容が書き換わる可能性があるので、__get__時に再検証を行うオプションmonitoring_overwriteを持ちます。
    入れ子構造のコンテナバリデータは、親の検証が行われる際に検証されてしまうので、このオプションは実質的に親の設定が伝播します。
    """
    def __init__(self, TEMPLATE: Any, monitoring_overwrite: bool = True, allow_convert: bool = True):
        """雛形、アクセス時に再検証を行うか、変換を許可するかを設定してバリデータを生成します。

        変換を許可する場合、元のコンテナまたはコンテナ内の要素は異なるidを持つ場合があります。

        Args:
            TEMPLATE (Any): 雛形です。継承後のクラスによって異なります。
            monitoring_overwrite (bool, optional): アクセス時に再検証を行うかどうかです。要素数などによっては時間がかかる場合があります。不変であることが保証されている場合には無効にしてください。
            allow_convert (bool, optional): コンバータによる要素の変換を許可するかどうかです。
        """
        self.TEMPLATE = TEMPLATE
        self.monitoring_overwrite = monitoring_overwrite
        self.allow_convert = allow_convert

    def __get__(self, instance, otype):
        res = super().__get__(instance, otype)
        if self.monitoring_overwrite:
            res = self.validate(res)
        return res


class Converter(Validator):
    """すべてのコンバータの基底クラスです。

    バリデータとこのクラスを継承してsuper_validateメソッドを定義してください。
    """
    @abstractmethod
    def super_validate(self, value: Any) -> Any:
        """スーパークラスのvalidateを使用して検証を行います。

        即ち、変換を行いたくない場合に使用します。
        このメソッドはコンテナバリデータ等で中身の変換を拒否したい場合に使用されます。

        Args:
            value (Any): 検証する値です。

        Returns:
            Any: 検証を通過した値です。
        """
        pass


class CNoneable(Converter):
    """バリデータまたはコンバータにNoneを含めることを許可するクラスです。
    """
    def __init__(self, validator: Union[Validator, Converter], monitoring_overwrite: bool = True):
        """バリデータ、コンバータのインスタンスを渡し、追加でNoneを許可するようにします。

        Args:
            validator (Union[Validator, Converter]): バリデータまたはコンバータです。
            monitoring_overwrite (bool, optional): アクセス時に再検証を行うかどうかです。要素数などによっては時間がかかる場合があります。不変であることが保証されている場合には無効にしてください。
        """
        self.validator = validator
        self.monitoring_overwrite = monitoring_overwrite

    def __get__(self, instance, otype):
        res = super().__get__(instance, otype)
        if res is None:
            return res
        if getattr(self.validator, 'monitoring_overwrite', None):
            res = self.validator.validate(res)
        return res

    def validate(self, value: Any) -> Any:
        """Noneを通し、それ以外を本来のvalidator.validateを使用して検証を行います。

        Args:
            value (Any): 検証する値です。

        Returns:
            Any: 検証を通過した値です。
        """
        if value is None:
            return None
        return self.validator.validate(value)

    def super_validate(self, value: Any) -> Any:
        """Noneを通し、それ以外を本来のvalidator.super_validateを使用して検証を行います。

        validatorがコンバータでない場合、validator.validateを使用して検証を行います。

        Args:
            value (Any): 検証する値です。

        Returns:
            Any: 検証を通過した値です。
        """
        if value is None:
            return None
        if isinstance(self.validator, Converter):
            return self.validator.super_validate(value)
        self.validator.validate(value)


class CNumerical(Converter):
    """数値型用コンバータの基底クラスです。

    (int, float)に変換を試みるメソッドが定義されています。

    Args:
        Converter ([type]): [description]
    """
    @staticmethod
    def try_int(value: Any) -> Optional[int]:
        """intへの変換を試みます。

        Args:
            value (Any): 変換を試みたい値です。

        Returns:
            Optional[int]: int変換されたvalueまたはNoneです。
        """
        if type(value) is int:
            return value
        try:
            return int(value)
        except:
            try:
                return int(float(value))
            except:
                return None

    @staticmethod
    def try_float(value: Any) -> Optional[float]:
        """floatへの変換を試みます。

        Args:
            value (Any): 変換を試みたい値です。

        Returns:
            Optional[float]: float変換されたvalueまたはNoneです。
        """
        if type(value) is float:
            return value
        try:
            return float(value)
        except:
            try:
                return float(int(value))
            except:
                return None
