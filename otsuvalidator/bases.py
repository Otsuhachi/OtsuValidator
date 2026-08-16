__all__ = (
    "Converter",
    "Validator",
    "VChain",
    "VContainer",
)
from abc import ABC, abstractmethod
from typing import Any, Literal, Self, overload


class Validator[OutT](ABC):
    def __init__(self) -> None:
        self.public_name: str = ""
        self.private_name: str = ""

    def __set_name__(self, owner: type[Any], name: str) -> None:
        """クラス定義時に自動的に呼び出される。

        例: `age = Validator()`と書くと`name`に"age"が入る。
        """
        self.public_name = name
        self.private_name = f"_{name}"

    @overload
    def __get__(self, instance: None, owner: type[Any]) -> Self: ...

    @overload
    def __get__(self, instance: Any, owner: type[Any]) -> OutT: ...
    def __get__(self, instance: Any | None, owner: type[Any]) -> OutT | Self:
        # クラス属性としてアクセスされた場合
        # 例: MyClass.age
        if instance is None:
            return self
        # インスタンス属性としてアクセスされた場合
        # myc_instance.age
        return getattr(instance, self.private_name)

    def set_name(self, name: str) -> None:
        """バリデータの表示名を動的に設定する。"""
        self.public_name = name
        self.private_name = f"_{name}"

    @abstractmethod
    def validate(self, value: Any) -> OutT:
        """
        [抽象メソッド] 子クラスで必ず実装する必要がある。
        値が正しければその値を返し、不正なら例外を投げる。
        """
        raise NotImplementedError()

    def __set__(self, instance: Any, value: Any) -> None:
        """値を代入する際に呼び出される。

        `validate`メソッドでチェックを通った値のみ保持する。
        """
        # 1. 値を検証(子クラスの実装を呼び出す。)
        validated_value = self.validate(value)
        # 2. private_nameでインスタンスに保存
        setattr(instance, self.private_name, validated_value)

    def __or__[NextOutT](self, other: "Validator[NextOutT]") -> "VChain[NextOutT]":
        """パイプ演算子によるバリデータの直列連結をサポートする。"""
        return VChain(self, other)


class Converter[InT, OutT](Validator[OutT]):
    """値を特定の型や形式に変換するディスクリプタの基底クラス。"""

    @abstractmethod
    def validate(self, value: InT) -> OutT:
        """入力値を変換して返すロジックを実装する。"""
        raise NotImplementedError()

    def super_validate(self, value: Any) -> OutT:
        """変換を行わず、スーパークラスの検証のみを行う。"""
        return super().validate(value)  # type: ignore


class VChain[OutT](Validator[OutT]):
    """複数のバリデータを直列に実行するクラス。"""

    def __init__(self, *validators: Validator[Any], pass_type: Literal["all", "any"] = "any") -> None:
        super().__init__()
        self.validators: tuple[Validator[Any], ...] = validators
        self.pass_type: Literal["all", "any"] = pass_type

    def validate(self, value: Any) -> OutT:
        current_value = value
        validators = self.validators
        if self.pass_type == "all":
            for validator in validators:
                current_value = validator.validate(current_value)
        else:
            passed = False
            exceptions = []
            for validator in validators:
                try:
                    tmp = validator.validate(current_value)
                    current_value = tmp
                    passed = True
                except Exception as ex:
                    exceptions.append(ex)
            if not passed:
                raise ValueError(*exceptions)
        return current_value

    def __or__[NextOutT](self, other: Validator[NextOutT]) -> "VChain[NextOutT]":
        return VChain(*self.validators, other)


class VContainer[OutT](Validator[OutT]):
    """
    VDict, VList, VTuple などの構造を持つバリデータの基底クラス。
    スキーマの保持や、動的な再検証フラグの管理を行う。
    """

    def __init__(
        self,
        schema: Any,
        *,
        monitoring_overwrite: bool = False,
    ) -> None:
        super().__init__()
        self.schema = schema
        self.monitoring_overwrite = monitoring_overwrite

    def __get__(self, instance: Any | None, owner: type[Any]) -> OutT | Self:  # type: ignore
        """
        monitoring_overwrite が True の場合、
        値を取得する際にも再検証を実行するようにオーバーライド。
        """
        if instance is None:
            return self
        value = getattr(instance, self.private_name)
        if self.monitoring_overwrite:
            return self.validate(value)
        return value
