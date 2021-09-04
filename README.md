-   [概要](#概要)
    -   [インストール](#インストール)
    -   [モジュール](#モジュール)
    -   [継承規則](#継承規則)
    -   [実行例](#実行例)

# 概要

このライブラリは値の正常性を検証するバリデータ群と、検証前に型変換を試みるコンバータ群です。
ディスクリプタとして使用することで属性に不正な値が代入されるのを防止します。
また、単独で使用することも可能です。

このライブラリは以下の環境で作成されています。
`Windows10(64bit)`, `Python3.8`
**`:=演算子`を使用しているので、3.8以前のバージョンでは使えません。**

## インストール

インストール

`pip install otsuvalidator`

アップデート

`pip install -U otsuvalidator`

アンインストール

`pip uninstall otsuvalidator`

## モジュール

モジュールは以下の3つが存在します。

|               モジュール名               | 概要                                                 |
| :--------------------------------: | :------------------------------------------------- |
|      [bases](#basesモジュールのクラス)      | バリデータ、コンバータの基底クラスが定義されている<br>自作のバリデータを定義するときに使用できる |
| [validators](#validatorsモジュールのクラス) | バリデータが定義されている                                      |
| [converters](#convertersモジュールのクラス) | コンバータが定義されている                                      |

### basesモジュールのクラス

|     クラス    | 概要                                                                                    |
| :--------: | :------------------------------------------------------------------------------------ |
|  Validator | すべてのバリデータ、コンバータの基底クラス                                                                 |
| VContainer | コンテナ用のバリデータの基底クラス<br>中身が可変なクラスのバリデータを定義するときに使用する                                      |
|  Converter | コンバータの基底クラス<br>セキュアさが重視される場面では使用しない                                                   |
| CNumerical | 数値型用コンバータの基底クラス<br>`value`に対し、`int`変換、`float`変換を試みるメソッドが定義されている<br>`complex`は想定されていない |

### validatorsモジュールのクラス

スーパークラスの表記がないものは`Validator`を継承しています。

|   クラス   |   スーパークラス  | 概要                 |     期待する型    |
| :-----: | :--------: | :----------------- | :----------: |
|  VBool  |            | 真偽値オブジェクトか         |     bool     |
| VChoice |            | 選択肢の中から1つが選択されているか |      Any     |
| VNumber |            | 適切な数値か             |  int, flaot  |
|  VFloat |   VNumber  | 適切な浮動小数点数か         |     flaot    |
|   VInt  |   VNumber  | 適切な整数か             |      int     |
|  VPath  |            | 適切なパスか             | pathlib.Path |
| VString |            | 適切な文字列か            |      str     |
|  VRegex |   VString  | 正規表現にマッチする適切な文字列か  |      str     |
|  VDict  | VContainer | 適切な辞書か             |     dict     |
|  VList  | VContainer | 適切なリストか            |     list     |
|  VTuple |  VContaner | 適切なタプルか            |     tuple    |

### convertersモジュールのクラス

スーパークラスにコンバータが記載されていないクラスは`Converter`を継承しています。

|   クラス   |       スーパークラス       | 概要                                                                                             |
| :-----: | :-----------------: | :--------------------------------------------------------------------------------------------- |
|  CBool  |   VBool, Converter  | 一般に**Yes/Noとして解釈できる値**に対し、bool変換を試み、検証を行う<br>`bool(value)`では`True`になるものが`False`になったり例外が発生したりする |
| CNumber | VNumber, CNumerical | `int`, `float`型への変換を試み、検証を行う                                                                   |
|  CFloat |  VFloat, CNumerical | `float`型への変換を試み、検証を行う                                                                          |
|   CInt  |   VInt, CNumerical  | `int`型への変換を試み、検証を行う                                                                            |
|  CPath  |   VPath, Converter  | `Path`型への変換を試み、検証を行う                                                                           |
| CString |  VString, Converter | `str`型への変換を試み、検証を行う                                                                            |

## 継承規則

きちんと動作するバリデータ、コンバータを定義するために規則です。

-   [Validator継承規則](#validator継承規則)
-   [VContainer継承規則](#vcontainer継承規則)
-   [Converter継承規則](#converter継承規則)

### Validator継承規則

|  規則 | 概要                                      | 理由                    |
| :-: | :-------------------------------------- | :-------------------- |
|  命名 | クラス名は`V{検証したいクラス名}`とする                  | 管理のしやすさ               |
|  継承 | `Validator`を継承する                        |                       |
|  定義 | `validate`メソッドを定義し、検証が通った場合には`value`を返す | 拡張してコンバータを定義するときに必要   |
|  変換 | `value`の型を変換しない                         | 変換と検証を行う場合はコンバータを使用する |

### VContainer継承規則

|  規則 | 概要                                                                                                | 理由                                              |
| :-: | :------------------------------------------------------------------------------------------------ | :---------------------------------------------- |
|  命名 | クラス名は`V{検証したいクラス名}`とする                                                                            | 管理のしやすさ<br>本質的にはValidatorと変わらないので規則もそのまま適用      |
|  継承 | `VContainer`を継承する                                                                                 |                                                 |
|  定義 | `validate`メソッドを定義し、検証が通った場合には`value`を返す<br>変換を許可する場合、`TEMPLATE`が`Validator`以外の場合など細かな違いを設定する必要がある | コンテナそのものの検証と中身の検証が必要                            |
|  変換 | `value`の型を変換しない<br>`value`の各要素`v`に対してはオプション次第                                                     | `TEMPLATE`にコンバータを渡している場合、禁止されていない限り変換を行うのが自然なため |

### Converter継承規則

`CNumerical`についてもここに従ってください。

|  規則 | 概要                                                                                                          | 理由                                                   |
| :-: | :---------------------------------------------------------------------------------------------------------- | :--------------------------------------------------- |
|  命名 | クラス名は`C{変換検証したいクラス名}`とする                                                                                    | 一目で変換を行うクラスと認識するため                                   |
|  継承 | `(検証したいクラスのバリデータ, コンバータ)`を継承する                                                                              | `検証したいクラスのバリデータ.validate`メソッドを`validate`メソッド内で呼び出すため |
|  定義 | `validate`メソッドを定義し、変換検証が通った場合には変換された`value`を返す<br>`super_validate`メソッドを定義し、`検証したいクラス.validate`メソッドを行えるようにする | VContainerなど、変換を許可したくない状況では`super_validate`を使用するため   |
|  変換 | `validate`メソッド内で変換を試みる<br>`super_validate`メソッドでは変換しない                                                       | 定義で書いた通り無変換が必要になる場面もあるため                             |

## 実行例

### バリデータの実行例

バリデータをディスクリプタとして使用している`Student`クラスを試しに使用します。
#### バリデータの実行例目次
- [前提コード](#バリデータ実行例-前提コード)
- [nameの操作](#バリデータ実行例-nameの操作)
- [ageの操作](#バリデータ実行例-ageの操作)
- [genderの操作](#バリデータ実行例-genderの操作)
- [gradesの操作](#バリデータ実行例-gradesの操作)
#### バリデータ実行例-前提コード

[目次](#バリデータの実行例目次)に戻る

説明は以下の条件を満たした環境で実行されることを想定しています。

1. Python3.8以上がインストールされたWindows
2. 本ライブラリがインストールされている
3. 以下の`test.py`ファイルを生成し、`py -i test.py`、または`対話モード`で以下のコードが入力されている

```python
# test.py
from otsuvalidator import VChoice, VDict, VInt, VString


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

    def show_profile(self):
        name = self.name
        age = self.age
        gender = self.gender
        grades = self.grades
        japanese = grades['Japanese']
        social = grades['Social Studies']
        math = grades['Math']
        profiles = ('名前', '年齢', '性別', '国語', '社会', '数学')
        profile_values = (name, age, gender, japanese, social, math)
        for title, value in zip(profiles, profile_values):
            print(f'{title}: {value}')


otsuhachi = Student()
```

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

#### バリデータ実行例-gradesの操作

[目次](#バリデータの実行例目次)に戻る

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

##### gradesの概要


一見複雑ですので分解して考えてみます。

- gradesが持つべきキーは(`Japanese`, `Social Studies`, `Math`)の3つ
   - `Japanese`と`Social Studies`は`0～100`の整数値
   - `Math`は(`Math1`, `Math2`)のキーを持つ辞書
      - `Math1`と`Math2`は`0～100`の整数値
      - `allow_missing_key`が`True`なのでキーを持たない辞書でも可
      - `monitoring_overwrite`は`True`でも実質無関係
- `allow_missing_key`が`False`なので、キーすべてが含まれている必要がある
- `monitoring_overwrite`が`False`なので`otsuhachi.grades`をしても再検証が行われない

以上のような設定のバリデータになっています。

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
