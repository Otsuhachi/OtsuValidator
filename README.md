- [概要](#概要)
  - [インストール](#インストール)
  - [モジュール](#モジュール)
  - [継承規則](#継承規則)
  - [実行例-バリデータ](#実行例-バリデータ)
  - [コンバータの変換](#コンバータの変換)
    - [実行例-コンバータ](#実行例-コンバータ)
  - [cast](#cast)

# 概要

このライブラリは値の正常性を検証するバリデータ群と、検証前に型変換を試みるコンバータ群です。  
ディスクリプタとして使用することで属性に不正な値が代入されるのを防止します。  
また、単独で使用することも可能です。  

このライブラリは以下の環境で作成されています。  
`Windows10(64bit)`, `Python3.7.9`  

## インストール

インストール

`pip install otsuvalidator`

アップデート

`pip install -U otsuvalidator`

アンインストール

`pip uninstall otsuvalidator`

## モジュール

モジュールは以下の3つが存在します。

モジュール名|概要
:--:|--
[bases](#basesモジュールのクラス)|バリデータ、コンバータの基底クラスが定義されいる<br>自作のバリデータを定義するときに使用できる
[validators](#validatorsモジュールのクラス)|バリデータが定義されている
[converters](#convertersモジュールのクラス)|コンバータが定義されている


omit in toc
<!-- omit in toc -->
### basesモジュールのクラス

`Validator`と表記されている部分に関しては、バリデータ、コンバータ両方を指します。

クラス|概要
:--:|:--
Validator|すべてのバリデータ、コンバータの基底クラス
VContainer|コンテナ用のバリデータの基底クラス<br>中身が可変なクラスのバリデータを定義するときに使用する
Converter|コンバータの基底クラス<br>セキュアさが重視される場面では使用しない
CNoneable|`Validator`既定のバリデーションに加え、`None`を許可する<br>変換の可否は以下の2点に依存する<br>-渡した`Validator`がコンバータか否か<br>-所属する`VContainer`の`allow_convert`オプション
CNumerical|数値型用コンバータの基底クラス<br>`value`に対し、`int`変換、`float`変換を試みるメソッドが定義されている<br>`complex`は想定されていない

<!-- omit in toc -->
### validatorsモジュールのクラス

スーパークラスの表記がないものは`Validator`を継承しています。

クラス|スーパークラス|概要|期待する型
:--:|:--:|:--|:--:
VBool||真偽値オブジェクトか|bool
VChoice||選択肢の中から1つが選択されているか|Any
VNumber||適切な数値か|int,flaot
VFloat|VNumber|適切な浮動小数点数か|flaot
VInt|VNumber|適切な整数か|int
VPath||適切なパスか|pathlib.Path
VString||適切な文字列か|str
VRegex|VString|正規表現にマッチする適切な文字列か|str
VDict|VContainer|適切な辞書か|dict
VList|VContainer|適切なリストか|list
VTuple|VContaner|適切なタプルか|tuple
VTimedelta||適切な経過時間型か|datetime.timedelta

<!-- omit in toc -->
### convertersモジュールのクラス

スーパークラスにコンバータが記載されていないクラスは`Converter`を継承しています。

クラス|スーパークラス|概要
:--:|:--:|:--
CBool|VBool,Converter|一般に**Yes/Noとして解釈できる値**に対し、bool変換を試み、検証を行う<br>`bool(value)`では`True`になるものが`False`になったり例外が発生したりする
CNumber|VNumber, CNumerical|`int`,`float`型への変換を試み、検証を行う
CFloat|VFloat, CNumerical|`float`型への変換を試み、検証を行う
CInt|VInt, CNumerical|`int`型への変換を試み、検証を行う
CPath|VPath, Converter|`Path`型への変換を試み、検証を行う
CString|VString, Converter|`str`型への変換を試み、検証を行う
CTimedelta|VTimedelta, Converter|`datetime.timedelta`型への変換を試み、検証を行う

## 継承規則

きちんと動作するバリデータ、コンバータを定義するための規則です。  
`CNoneable`は**継承しないでください。**

<!-- no toc -->
-   [Validator継承規則](#validator継承規則)
-   [VContainer継承規則](#vcontainer継承規則)
-   [Converter継承規則](#converter継承規則)

<!-- omit in toc -->
### Validator継承規則

規則|概要|理由
:--:|:--|:--
命名|クラス名は`V{検証したいクラス名}`とする|管理のしやすさ
継承|`Validator`を継承する|
定義|`validate`メソッドを定義し、検証が通った場合には`value`を返す|拡張してコンバータを定義するときに必要
変換|`value`の型を変換しない|変換と検証を行う場合はコンバータを使用する

<!-- omit in toc -->
### VContainer継承規則

規則|概要|理由|
:--:|:--|:--
命名|クラス名は`V<検証したいクラス名>`とする|管理のしやすさ<br>本質的にはValidatorと変わらないので規則もそのまま適用
継承|`VContainer`を継承する|
定義|`validate`メソッドを定義し、検証が通った場合には`value`を返す<br>変換を許可する場合、`TEMPLATE`が`Validator`以外の場合など細かな違いを設定する必要がある|コンテナそのものの検証と中身の検証が必要
変換|`value`の型を変換しない<br>`value`の各要素`v`に対してはオプション次第|`TEMPLATE`にコンバータを渡している場合、禁止されていない限り変換を行うのが自然なため

<!-- omit in toc -->
### Converter継承規則

`CNumerical`についてもここに従ってください。

規則|概要|理由
:--:|:--|:--
命名|クラス名は`C<変換検証したいクラス名>`とする|一目で変換を行うクラスと認識するため
継承|`(検証したいクラスのバリデータ,コンバータ)`を継承する|`検証したいクラスのバリデータ.validate`メソッドを`validate`メソッド内で呼び出すため
定義|`validate`メソッドを定義し、変換検証が通った場合には変換された`value`を返す<br>`super_validate`メソッドを定義し、`検証したいクラス.validate`メソッドを行えるようにする|VContainerなど、変換を許可したくない状況では`super_validate`を使用するため
変換|`validate`メソッド内で変換を試みる<br>`super_validate`メソッドでは変換しない|定義で書いた通り無変換が必要になる場面もあるため

## 実行例-バリデータ

<!-- omit in toc -->
### バリデータの実行例

バリデータをディスクリプタとして使用している`Student`クラスを試しに使用します。
<!-- omit in toc -->
#### バリデータの実行例目次

<!-- no toc -->
- [前提コード](#バリデータ実行例-前提コード)
- [nameの操作](#バリデータ実行例-nameの操作)
- [ageの操作](#バリデータ実行例-ageの操作)
- [genderの操作](#バリデータ実行例-genderの操作)
- [gradesの操作](#バリデータ実行例-gradesの操作)
- [hobbyの操作](#バリデータ実行例-hobbyの操作)
- [addressの操作](#バリデータ実行例-addressの操作)
- [成功](#バリデータ実行例-成功)

<!-- omit in toc -->
#### バリデータ実行例-前提コード

[目次](#バリデータの実行例目次)に戻る

説明は以下の条件を満たした環境で実行されることを想定しています。

1. Python3.8以上がインストールされたWindows
2. 本ライブラリがインストールされている
3. 以下の`test.py`ファイルを生成し、`py -i test.py`、または`対話モード`で以下のコードが入力されている

```python
# test.py
from otsuvalidator import (CNoneable, VChoice, VDict, VInt, VList, VRegex, VString)


class Student:
    name = VString(1, 50, checker=str.istitle)  # 1文字以上50文字以下, str.istitleがTrueになる文字列
    age = VInt(0, 150)  # 0以上150以下の整数
    gender = VChoice('male', 'female', 'others')  # (male, female, others)のいずれか
    grades = VDict(
        # 以下の構造を持つ辞書, キー欠落不可, アクセス時に再検証を行わない
        {
            'Japanese':
            VInt(0, 100),  # 0以上100以下の整数
            'Social Studies':
            VInt(0, 100),
            'Math':
            VDict(
                # 以下のキーを持つ辞書, キー欠落可, アクセス時に再検証を行う
                {
                    'Math1': VInt(0, 100),
                    'Math2': VInt(0, 100)
                },
                allow_missing_key=True,
                monitoring_overwrite=True,
            )
        },
        allow_missing_key=False,
        monitoring_overwrite=False,
    )
    # 1文字以上の文字列だけのリスト Noneで無回答可 要素数は無制限
    hobby = CNoneable(VList(VString(1)))
    # [郵便番号, 都道府県, 市町村群]のリスト Noneで無回答可
    address = CNoneable(VList([VRegex('^\\d{3}-?\\d{4}$'), VRegex('(?!.*\\d.*)'), VRegex('(?!.*\\d.*)')]))

    def show_profile(self):
        name = self.name
        age = self.age
        gender = self.gender
        grades = self.grades
        japanese = grades['Japanese']
        social = grades['Social Studies']
        math = grades['Math']
        hobby = self.hobby
        address = self.address
        profiles = ('名前', '年齢', '性別', '国語', '社会', '数学', '趣味', '住所')
        profile_values = (name, age, gender, japanese, social, math, hobby, address)
        for title, value in zip(profiles, profile_values):
            print(f'{title}: {value}')


otsuhachi = Student()
```

<!-- omit in toc -->
#### バリデータ実行例-nameの操作

[目次](#バリデータの実行例目次)に戻る

`otsuhachi.name`を操作します。  
`Student`の`name`属性は`VString(1, checker=str.istitle)`によって検証されます。

```python

# 失敗 (型が異なる)
>>> otsuhachi.name = 28
Traceback (most recent call last):
...
TypeError: 属性'name'はstr型である必要があります。(28: int)

# 失敗 (最低文字数を満たしていない)
>>> otsuhachi.name = ''
Traceback (most recent call last):
...
ValueError: 属性'name'は1文字以上である必要があります。('': str)

# 失敗 (最大文字数を超過している)
>>> otsuhachi.name = 'A' + ('a' * 100)
Traceback (most recent call last):
...
ValueError: 属性'name'は50文字以下である必要があります。('Aaaaaaaaa...aaaaaaaaa': str)

# 失敗 (checkerがTrueを返さない)
>>> otsuhachi.name = 'otsuhachi'
Traceback (most recent call last):
...
ValueError: 属性'name'は指定した形式に対応している必要があります。<method 'istitle' of 'str' objects>。('otsuhachi': str)

# 成功
>>> otsuhachi.name = 'Otsuhachi'
>>> otsuhachi.name
'Otsuhachi'
```

<!-- omit in toc -->
#### バリデータ実行例-ageの操作

[目次](#バリデータの実行例目次)に戻る

`otsuhachi.age`を操作します。  
`Student`の`age`属性は`VInt(0)`によって検証されます。

```python

#失敗 (型が異なる)
>>> otsuhachi.age = 28.8
Traceback (most recent call last):
...
TypeError: 属性'age'はint型である必要があります。(28.8: float)

# 失敗 (最小値未満)
>>> otsuhachi.age = -1
...
ValueError: 属性'age'は0より小さい値を設定することはできません。(-1: int)

# 失敗 (最大値超過)
>>> otsuhachi.age = 280
Traceback (most recent call last):
...
ValueError: 属性'age'は150より大きい値を設定することはできません。(280: int)

# 成功
>>> otsuhachi.age = 28
>>> otsuhachi.age
28
```

<!-- omit in toc -->
#### バリデータ実行例-genderの操作

[目次](#バリデータの実行例目次)に戻る

`otsuhachi.gender`を操作します。  
`Student`の`gender`属性は`VChoice('male', 'female', 'others')`によって検証されます。


```python

# 失敗 (選択肢にない値)
>>> otsuhachi.gender = None
Traceback (most recent call last):
...
ValueError: 属性'gender'は{'male', 'others', 'female'}のいずれかである必要があります。(None: NoneType)

# 失敗 (選択肢にない値)
>>> otsuhachi.gender = 'mal'
Traceback (most recent call last):
...
ValueError: 属性'gender'は{'male', 'others', 'female'}のいずれかである必要があります。('mal': str)

# 成功
>>> otsuhachi.gender = 'others'
>>> otsuhachi.gender
'others'
>>> otsuhachi.gender = 'female'
>>> otsuhachi.gender
'female'
>>> otsuhachi.gender = 'male'
>>> otsuhachi.gender
'male'
```

<!-- omit in toc -->
#### バリデータ実行例-gradesの操作

[目次](#バリデータの実行例目次)に戻る

<!-- no toc -->
- [gradesの概要](#gradesの概要)
- [gradesの基本的な失敗と成功の例](#gradesの基本的な失敗と成功の例)
- [gradesで起こりえる不正](#gradesで起こりえる不正)
- [gradesで起こりえる不正の防止](#gradesで起こりえる不正の防止)

`otsuhachi.garades`を操作します。  
`Student`の`grades`は以下のように定義されたバリデータによって検証されます。

```python

VDict(
    {
        'Japanese': VInt(0, 100),
        'Social Studies': VInt(0, 100),
        'Math': VDict(
            {
                'Math1': VInt(0, 100),
                'Math2': VInt(0, 100)
            },
            allow_missing_key=True,
            monitoring_overwrite=True,
        )
    },
    allow_missing_key=False,
    monitoring_overwrite=False,
)
```

<!-- omit in toc -->
##### gradesの概要


分解して考えてみます。

- gradesが持つべきキーは(`Japanese`, `Social Studies`, `Math`)の3つ
   - `Japanese`と`Social Studies`は`0～100`の整数値
   - `Math`は(`Math1`, `Math2`)のキーを持つ辞書
      - `Math1`と`Math2`は`0～100`の整数値
      - `allow_missing_key`が`True`なのでキーを持たない辞書でも可
      - `monitoring_overwrite`は`True`でも実質無関係
- `allow_missing_key`が`False`なので、キーすべてが含まれている必要がある
- `monitoring_overwrite`が`False`なので`otsuhachi.grades`をしても再検証が行われない

以上のような設定のバリデータになっています。

<!-- omit in toc -->
##### gradesの基本的な失敗と成功の例

```python

# 失敗 (型が異なる)
>>> otsuhachi.grades = ['Japanese', 'Social Studies', 'Math']
Traceback (most recent call last):
...
TypeError: 属性'grades'はdict型である必要があります。(['Japanese', 'Social Studies', 'Math']: list)

# 失敗 (必須キーの欠落)
>>> otsuhachi.grades = {'Japanese': 68}
Traceback (most recent call last):
...
ValueError: 属性'grades'は以下のキーを設定する必要があります。({'Math', 'Social Studies'})。({'Japanese': 68}: dict)

# 失敗 (不正な値)
>>> otsuhachi.grades = {'Japanese': 68, 'Social Studies': 28, 'Math': 66}
Traceback (most recent call last):
...
TypeError: dict型である必要があります。(66: int)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
...
TypeError: キー'Math'は不正な値です。(66: int)

# 失敗 (不正な値: 入れ子構造)
>>> otsuhachi.grades = {'Japanese': 68, 'Social Studies': 28, 'Math': {'Math1': 2.8}}
Traceback (most recent call last):
...
TypeError: int型である必要があります。(2.8: float)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
...
TypeError: キー'Math1'は不正な値です。(2.8: float)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
...
TypeError: キー'Math'は不正な値です。({'Math1': 2.8}: dict)

# 失敗 (未定義のキー)
>>> otsuhachi.grades = {'Japanese': 68, 'Social Studies': 28, 'Math': {'Math1': 66}, 'Science': 70}
Traceback (most recent call last):
...
ValueError: 属性'grades'は以下のキーを設定することはできません。({'Science'})。({'Japanese...ence': 70}: dict)

# 成功
>>> otsuhachi.grades = {'Japanese': 68, 'Social Studies': 28, 'Math': {'Math1': 66, 'Math2': 56}}
>>> otsuhachi.grades
{'Japanese': 68, 'Social Studies': 28, 'Math': {'Math1': 66, 'Math2': 56}}

# Math内はキー欠落可
>>> otsuhachi.grades = {'Japanese': 68, 'Social Studies': 28, 'Math': {'Math1': 66}}
>>> otsuhachi.grades
{'Japanese': 68, 'Social Studies': 28, 'Math': {'Math1': 66}}
```

<!-- omit in toc -->
##### gradesで起こりえる不正

この設定では書き換えに対して無力です。  
`otsuhachi.grades`が呼び出されたとき限定で検証が行われるので、以下のような操作では不正が行えます。

```python

# 正常な形式でgradesをセット
>>> otsuhachi.grades = {'Japanese': 68, 'Social Studies': 28, 'Math': {'Math1': 66, 'Math2': 56}}
>>> otsuhachi.grades
{'Japanese': 68, 'Social Studies': 28, 'Math': {'Math1': 66, 'Math2': 56}}

# grades['Math']を66にする
>>> otsuhachi.grades['Math'] = 66
>>> otsuhachi.grades
{'Japanese': 68, 'Social Studies': 28, 'Math': 66}
```

<!-- omit in toc -->
##### gradesで起こりえる不正の防止

不正の防止には主に2つの手段があります。

1. バリデータをクラス外で定義し、必要に応じて検証を行う
2. `monitoring_overwrite`を`True`にする

1.の方法では手間が掛かりますが、不要な時に検証されることがないので比較的高速な動作が期待されます。  
また`monitoring_overwrite`は`False`でなければ2の方法と変わりありません。  

2.の方法では`otsuhachi.grades`が呼ばれるたびに検証されるので手軽です。  

どちらも書き換えは許してしまいますが、最終的に値を利用するタイミングでは検証が行われます。

```python

# 1の方法
GRADES_VALIDATOR = VDict(
    {
        'Japanese': VInt(0, 100),
        'Social Studies': VInt(0, 100),
        'Math': VDict(
            {
                'Math1': VInt(0, 100),
                'Math2': VInt(0, 100)
            },
            allow_missing_key=True,
            monitoring_overwrite=True,
        )
    },
    allow_missing_key=False,
    monitoring_overwrite=False,
)

class Student:
    # ...部分は前提コード通りです。
    ...
    grades = GRADES_VALIDATOR
    ...

# 値のセット
otsuhachi = Student()
otsuhachi.grades = {'Japanese': 68, 'Social Studies': 28, 'Math': {'Math1': 66, 'Math2': 56}}
>>> otsuhachi.grades
{'Japanese': 68, 'Social Studies': 28, 'Math': {'Math1': 66, 'Math2': 56}}

# 不正な書き換え
>>> otsuhachi.grades['Math'] = 66
>>> otsuhachi.grades
{'Japanese': 68, 'Social Studies': 28, 'Math': 66}

# 不正が困る場面
>>> GRADES_VALIDATOR.validate(otsuhachi.grades)
Traceback (most recent call last):
...
TypeError: dict型である必要があります。(66: int)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
...
TypeError: キー'Math'は不正な値です。(66: int)

```

```python

# 2の方法
class Student:
    # ...部分は前提コード通りです。
    ...
    grades = VDict(
        ...
        monitoring_overwrite=True,
    )
    ...
    
# 値のセット
otsuhachi = Student()
>>> otsuhachi.grades = {'Japanese': 68, 'Social Studies': 28, 'Math': {'Math1': 66, 'Math2': 56}}
>>> otsuhachi.grades
{'Japanese': 68, 'Social Studies': 28, 'Math': {'Math1': 66, 'Math2': 56}}

# 不正な書き換え
>>> otsuhachi.grades['Math'] = 66
>>> otsuhachi.grades
Traceback (most recent call last):
...
TypeError: dict型である必要があります。(66: int)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
...
TypeError: キー'Math'は不正な値です。(66: int)
```

<!-- omit in toc -->
#### バリデータ実行例-hobbyの操作

[目次](#バリデータの実行例目次)に戻る

`otsuhachi.hobby`を操作します。  
`Student`の`hobby`属性は`CNoneable(VList(VString(1)))`によって検証されます。

`CNoneable`はバリデータに`None`を許可するクラスです。  
今回は`otsuhachi.hobby`が`None`または`VList(VString(1))`の条件を満たす時に検証を通過します。

```python

# 失敗 (CNoneableはNoneを許可するだけで、初期値をNoneにはしない)
>>> otsuhachi.hobby
Traceback (most recent call last):
...
AttributeError: 'Student' object has no attribute '_hobby'

# 失敗 (不正な値)
>>> otsuhachi.hobby = 1
Traceback (most recent call last):
...
TypeError: list型である必要があります。(1: int)

# 失敗 (リスト内の値が不正)
>>> otsuhachi.hobby = [1]
Traceback (most recent call last):
...
TypeError: str型である必要があります。(1: int)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
...
TypeError: インデックス0は不正な値です。(1: int)

# 成功
>>> otsuhachi.hobby = None
>>> print(otsuhachi.hobby)
None

# 成功
>>> otsuhachi.hobby = ['PC', 'game']
>>> otsuhachi.hobby
['PC', 'game']

# 失敗 (不正な値を追加後に参照)
>>> otsuhachi.hobby.append(1)
>>> otsuhachi.hobby
Traceback (most recent call last):
...
TypeError: str型である必要があります。(1: int)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
...
TypeError: インデックス2は不正な値です。(1: int)
```


<!-- omit in toc -->
#### バリデータ実行例-addressの操作

[目次](#バリデータの実行例目次)に戻る

`otsuhachi.address`を操作します。  
`Student`の`address`属性は`CNoneable(VList([VRegex('^\\d{3}-?\\d{4}$'), VRegex('(?!.*\\d.*)')`によって検証されます。  
基本的な失敗例、成功例は[hobby](#バリデータ実行例-hobbyの操作)を参照してください。  
`address`属性の特殊な点は`VList`の`TEMPLATE`が`list型`である点です。  

`value[i]`が`TEMPLATE[i]`でそれぞれ検証されます。

```python

# 失敗 (要素数が足りていない)
>>> otsuhachi.address = []
Traceback (most recent call last):
...
ValueError: あと3個設定する必要があります。([]: list)

# 失敗 (要素数が多い)
>>> otsuhachi.address = ['', '', '', '']
Traceback (most recent call last):
...
ValueError: あと1個減らす必要があります。(['', '', '', '']: list)

# 失敗 (不正な値)
>>> otsuhachi.address = ['0000000000', 'Otsu Prefecture2', 'OtsuCity']
Traceback (most recent call last):
...
ValueError: 正規表現'^\\d{3}-?\\d{4}$'に対応している必要があります。('0000000000': str)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
...
ValueError: インデックス0は不正な値です。('0000000000': str)

# 失敗 (不正な値)
>>> otsuhachi.address = ['282-2828', 'Otsu Prefecture2', 'OtsuCity']
Traceback (most recent call last):
...
ValueError: 正規表現'(?!.*\\d.*)'に対応している必要があります。('Otsu Prefecture2': str)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
...
ValueError: インデックス1は不正な値です。('Otsu Prefecture2': str)


# 成功
>>> otsuhachi.address = ['282-2828', 'Otsu Prefecture', 'OtsuCity']
>>> otsuhachi.address
['282-2828', 'Otsu Prefecture', 'OtsuCity']
```

<!-- omit in toc -->
#### バリデータ実行例-成功

[目次](#バリデータの実行例目次)に戻る

すべてのバリデータでの検証が終われば、設計通りにクラスが動作します。

```python

>>> otsuhachi.name = 'Otsuhachi'
>>> otsuhachi.age = 28
>>> otsuhachi.gender = 'male'
>>> otsuhachi.grades = {'Japanese': 68, 'Social Studies': 28, 'Math': {'Math1': 66, 'Math2': 56}}
>>> otsuhachi.hobby = ['PC', 'game']
>>> otsuhachi.address = ['282-2828', 'Otsu Prefecture', 'OtsuCity']
>>> otsuhachi.show_profile()
名前: Otsuhachi
年齢: 28
性別: male
国語: 68
社会: 28
数学: {'Math1': 66, 'Math2': 56}
趣味: ['PC', 'game']
住所: ['282-2828', 'Otsu Prefecture', 'OtsuCity']
```

## コンバータの変換

基本的にコンバータは`C<対象の型名>`で、`<対象の型>(value)`で変換できるかどうかを試すのが基本になります。  
たとえば`CString`ならば`str(value)`を試みてから検証を行います。
しかし、コンバータによってはその基本に従わないものがあります。  
`CInt`は、`int(value)`できなかった場合に`int(float(value))`を試します(`CFloat`はその逆の動作です)。  
これはまだ理解しやすい変換ですが、以下の2つのコンバータは若干特殊な挙動の変換を行います。  
これは`json`ファイルや`標準入力`などで受け取った場合の変換処理を容易に行うためです。

<!-- omit in toc -->
### CTimedelta

このコンバータは`str`, `dict`, `list`, `tuple`いずれかの型である場合に`Timedelta`型に変換を試みます。  
変換に必要な形式は以下の通りです。

型|形式
:--|:--
str|`(<日>( )day(s, ))<時>:<分>:<秒>(.<ミリ秒>)`<br>`()`で囲まれた部分の有無は任意<br>要は`str(<timedeltaインスタンス>)`で変換された後の形式(厳密には日と時間の間の空白を問わないなど若干異なる)
dict|`timedelta(**value)`でインスタンスを生成できる形式
list, tuple|`timedelta(*value)`でインスタンスを生成できる形式

<!-- omit in toc -->
### CBool

このコンバータは以下の標準定義の項目を`bool`に変換します。  
また、自分で`True`になる値、`False`になる値を設定することも可能です。  
さらに、`f(value)`が真偽値を返す関数`f`のタプルを渡して判定することも可能です。

以下が標準定義の真偽値対応表です。
`str`型は`value.lower()`されたあとで判定されるので、大文字小文字を問いません。

型|True|False
:--:|:--:|:--:
bool|True|False
str|'true', 'yes', 'y', '1'|'false', 'no', 'n', '0'
int|1|0
float|1.0|0.0

### 実行例-コンバータ


```python

from datetime import timedelta
from typing import cast

from otsuvalidator import CBool, CTimedelta


class SampleClass:
    bool_dflt: bool = cast(bool, CBool())
    bool_user: bool = cast(bool, CBool(true_data=('はい', ), false_data=('いいえ', )))
    td_timedelta: timedelta = cast(timedelta, CTimedelta())
    td_str: timedelta = cast(timedelta, CTimedelta())
    td_tuple: timedelta = cast(timedelta, CTimedelta())
    td_dict: timedelta = cast(timedelta, CTimedelta())

    def show(self):
        keys = (
            'bool_dflt',
            'bool_user',
            'td_timedelta',
            'td_str',
            'td_tuple',
            'td_dict',
        )
        for k in keys:
            v = getattr(self, k)
            print(f'{k}: {v}({type(v).__name__})')


s = SampleClass()
td = timedelta(days=1, seconds=2, microseconds=3, milliseconds=4, minutes=5, hours=6, weeks=7)
# s.bool_dflt = 'はい'  # Error

# 一般にYes/Noとして解釈されるものはboolに変換
s.bool_dflt = 'yes'

# ユーザ定義のTrueなのでTrueになる
s.bool_user = 'はい'

# 無変換でtimedelta
s.td_timedelta = td

# 特定形式の文字列をtimedeltaに変換
s.td_str = '50 days, 0:0:1'

# 特定形式のタプル、リストをtimedeltaに変換
s.td_tuple = (1, 2, 3, 4, 5, 7)

# 特定形式の辞書をtimedeltaに変換
s.td_dict = {'seconds': 2, 'microseconds': 3, 'milliseconds': 4, 'minutes': 5, 'hours': 6}

# 属性名: str(属性)(属性の型)を出力
s.show()
```

```console

bool_dflt: True(bool)
bool_user: True(bool)
td_timedelta: 50 days, 6:05:02.004003(timedelta)
td_str: 50 days, 0:00:01(timedelta)
td_tuple: 1 day, 7:05:02.004003(timedelta)
td_dict: 6:05:02.004003(timedelta)
```


## cast

[ここ](#実行例-コンバータ)でクラス属性に`bool_dflt:bool = cast(bool, CBool())`として`bool_dflt`属性を`bool`として認識するようにしました。  
しかし、これでは`s.bool_dflt = 'はい'`の部分でlinterがエラーを表示するようになります。  
これは`property`のようにlinterでの型表示をいい感じにする方法がわからなかったので、苦肉の策となります。  

もちろん、アクセスするたびに`cast`してしまえばいい話ですが、面倒です。  
この方法では属性を代入するときにはエラーが出る代わりに、属性にアクセスする際に扱いやすくなるので、`cast`の使用は好みで使い分けてください。  

**残念ながら現状ではアクセスの利便性と代入時のエラーはトレードオフになります。**
