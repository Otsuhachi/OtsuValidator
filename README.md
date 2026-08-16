- [概要](#概要)
  - [インストール](#インストール)
  - [モジュール](#モジュール)
    - [basesモジュールのクラス](#basesモジュールのクラス)
    - [validatorsモジュールのクラス](#validatorsモジュールのクラス)
    - [convertersモジュールのクラス](#convertersモジュールのクラス)
  - [継承規則](#継承規則)
    - [Validator継承規則](#validator継承規則)
    - [VContainer継承規則](#vcontainer継承規則)
    - [Converter継承規則](#converter継承規則)

---
# 概要

このライブラリは、値の正常性を検証するバリデータ群と、検証前に型変換を試みるコンバータ群を提供するユーティリティです。  
ディスクリプタとしてクラス属性に使用することで不適切な値の代入を防止できるほか、単独の関数・オブジェクトとして値を検証・変換することも可能です。

---
## インストール

**インストール**
```bash
pip install otsuvalidator
```

**アップデート**
```bash
pip install -U otsuvalidator
```

**アンインストール**
```bash
pip uninstall otsuvalidator
```

## モジュール
本ライブラリは主に以下の3つのモジュールで構成されています。

モジュール名|概要
:--:|:--:
`bases`|バリデータ・コンバータの基底クラスを定義。自作のバリデータを作成する際に使用します。
`validators`|値の検証のみを行うバリデータ群が定義されています。
`converters`|型変換を試みた上で検証を行うコンバータ群が定義されています。


### basesモジュールのクラス
- `Validator`: すべてのバリデータおよびコンバータの基底クラス。
- `VContainer`: コンテナ（リストや辞書など）用バリデータの基底クラス。要素が可変なオブジェクトを検証する際に使用します。
- `Converter`: コンバータの基底クラス。
- `VChain`: バリデータ・コンバータの連結をサポートします。

### validatorsモジュールのクラス
※破線されたクラスは非推奨です。
クラス|概要|期待する型
:--:|:--:|:--:
VBool|真偽値オブジェクトか検証|bool
VChoice|規定の選択肢の中から1つが選択されているか検証|Any
VNumerical / ~~VNumber~~|適切な数値か検証|int / float
VFloat|適切な浮動小数点数か検証|float
VInt|適切な整数か検証|int
VPath|適切なパスか検証|pathlib.Path
VString|適切な文字列か検証|str
~~VRegex~~|適切な正規表現か検証。`VString(pattern=...)`に合併。|str
VDict|適切な構造の辞書か検証|dict
VList|適切なリストか検証|list
VTuple|適切なタプルか検証|tuple
VTimedelta|適切なtimedelta型か検証|datetime.timedelta

### convertersモジュールのクラス
※破線されたクラスは非推奨です。
クラス|概要
:--:|:--:
CBool|Yes / Noとして解釈できる値に対し`bool`型への変換を試みて検証
CNumerical / ~~CNumber~~|`int` / `float`型への自動変換を試みて検証
CFloat|`float`型への自動変換を試みて検証
CInt|`int`型への自動変換を試みて検証
CPath|`pathlib.Path`型への自動変換を試みて検証
CString|`str`型への返還を試みて検証
CTimedelta|`datetime.timedelta`型への自動変換を試みて検証

## 継承規則
自作のバリデータやコンバータを正しく定義するための規則です。

### Validator継承規則
1. 命名: クラス名は`V{検証したいクラス名}`とします（例: `VString`）。
2. 継承: `Validator`クラスを継承します。
3. 定義: `validate`メソッドを定義し、検証が成功した場合は受け取った`value`を返します。
4. 変換: `validate`内で`value`の型変換を行ってはいけません（変換を行う場合は`Converter`を使用）。

### VContainer継承規則
1. 命名: クラス名は`V{検証したいクラス名}`とします（例: `VList`）。
2. 継承: `VContainer`クラスを継承します。
3. 定義: `validate`メソッドを定義し、検証通過時は`value`を返します。中身の各要素への検証規則を設定します。
4. 変換: コンテナ自体の型変換は行いません。ただし要素に対してはオプション設定に応じます。

### Converter継承規則
1. 命名: `C{変換検証したいクラス名}`とします（例: `CInt`）。
2. 継承: `（対象クラスのバリデータ, Converter）`の順で多重継承します。
3. 定義: `validate`内で型変換を行い、`return super().validate(value)`で検証して返します。
