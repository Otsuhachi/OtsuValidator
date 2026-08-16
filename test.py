import io
import sys
import unittest
from typing import Any

from otsuvalidator import VChain, VChoice, VDict, VInt, VList, VNone, VString


class Student:
    name = VString(min_len=1, max_len=50, checker=str.istitle, pattern=r"^[a-zA-Z]+ [a-zA-Z]+$")  # 1~50文字, タイトルケース, 正規表現
    age = VInt(min_val=0, max_val=150)
    gender = VChain(pass_type="any") | VChoice(("male", "female")) | VNone()  # 選択肢
    grades = VDict[str, Any](
        {
            "Japanese": VInt(min_val=0, max_val=100),
            "Social Studies": VInt(min_val=0, max_val=100),
            "Math": VDict(
                {
                    "Math1": VInt(min_val=0, max_val=100),
                    "Math2": VInt(min_val=0, max_val=100),
                },
                allow_missing=True,
                monitoring_overwrite=True,
            ),
        },
        allow_missing=False,
        monitoring_overwrite=False,
    )
    hobby = VList[str](VString(min_len=1))  # 1文字以上の文字列リスト
    address = VList[str](
        [
            VString(pattern=r"^\d{3}-?\d{4}$"),
            VString(pattern=r"[a-zA-Z]+"),
            VString(pattern=r"[a-zA-Z]+"),
        ]
    )

    def show_profile(self) -> None:
        profiles = ("名前", "年齢", "性別", "国語", "社会", "数学", "趣味", "住所")
        values = (
            self.name,
            self.age,
            self.gender,
            self.grades["Japanese"],  # type: ignore
            self.grades["Social Studies"],  # type: ignore
            self.grades["Math"],  # type: ignore
            self.hobby,
            self.address,
        )
        for title, val in zip(profiles, values, strict=True):
            print(f"{title}: {val}")


class TestStudentValidators(unittest.TestCase):
    def setUp(self) -> None:
        """テスト対象のインスタンスを初期化"""
        self.student = Student()

    def test_name_validation(self) -> None:
        """name属性の検証"""
        with self.assertRaisesRegex(TypeError, "str型である必要があります"):
            self.student.name = 28
        with self.assertRaisesRegex(ValueError, "長さは1以上である必要があります"):
            self.student.name = ""
        with self.assertRaisesRegex(ValueError, "にマッチしません"):
            self.student.name = "otsuhachi"
        with self.assertRaisesRegex(ValueError, "カスタム検証に失敗しました"):
            self.student.name = "otsu hachi"
        self.student.name = "Otsu Hachi"
        self.assertEqual(self.student.name, "Otsu Hachi")

    def test_age_validation(self) -> None:
        """age属性の検証"""
        with self.assertRaisesRegex(TypeError, "int型"):
            self.student.age = 28.8
        with self.assertRaisesRegex(ValueError, "150以下である必要があります"):
            self.student.age = 151
        with self.assertRaisesRegex(ValueError, "0以上である必要があります"):
            self.student.age = -1
        self.student.age = 28
        self.assertEqual(self.student.age, 28)

    def test_gender_validation(self) -> None:
        """gender属性の検証"""
        with self.assertRaisesRegex(ValueError, "いずれかである必要があります"):
            self.student.gender = "mal"
        self.student.gender = None
        self.assertEqual(self.student.gender, None)
        self.student.gender = "female"
        self.assertEqual(self.student.gender, "female")

    def test_grades_validation(self) -> None:
        """grades属性の検証"""
        with self.assertRaisesRegex(KeyError, "必須キー.*が存在しません"):
            self.student.grades = {"Japanese": 68}
        invalid_grades = {
            "Japanese": 68,
            "Social Studies": 28,
            "Math": {"Math1": -1, "Math2": 56},
        }
        with self.assertRaisesRegex(ValueError, r"'grades\['Math'\]\['Math1'\]'は0以上"):
            self.student.grades = invalid_grades
        valid_grades = {
            "Japanese": 68,
            "Social Studies": 28,
            "Math": {"Math1": 66, "Math2": 56},
        }
        self.student.grades = valid_grades
        self.assertEqual(self.student.grades, valid_grades)

    def test_hobby_validation(self) -> None:
        """hobby属性の検証"""
        with self.assertRaisesRegex(TypeError, "list型である必要があります"):
            self.student.hobby = 1
        invalid_hobbies = ["PC", ""]
        with self.assertRaisesRegex(ValueError, "長さは1以上である必要があります"):
            self.student.hobby = invalid_hobbies
        valid_hobbies = ["PC", "Game"]
        self.student.hobby = valid_hobbies
        self.assertEqual(self.student.hobby, valid_hobbies)

    def test_address_validation(self) -> None:
        """address属性の検証"""
        with self.assertRaisesRegex(ValueError, r"要素数（\d+）が定義されたスキーマの数（\d+）と一致しません"):
            self.student.address = []
        invalid_address = ["282-288", "Otsu Prefecture", "OtsuCity"]
        with self.assertRaisesRegex(ValueError, "にマッチしません"):
            self.student.address = invalid_address
        valid_address = ["282-2828", "Otsu Prefecture", "OtsuCity"]
        self.student.address = valid_address
        self.assertEqual(self.student.address, valid_address)

    def test_success_pattern(self) -> None:
        """正常系の統合テストと出力内容の確認"""
        student = self.student
        student.name = "Otsu Hachi"
        student.age = 28
        student.gender = "male"
        student.grades = {
            "Japanese": 68,
            "Social Studies": 28,
            "Math": {
                "Math1": 66,
                "Math2": 56,
            },
        }
        student.hobby = ["PC", "Game"]
        student.address = ["282-2828", "Otsu Prefecture", "OtsuCity"]

        # プロフィール出力のテスト
        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            student.show_profile()
        finally:
            sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("名前: Otsu Hachi", output)
        self.assertIn("年齢: 28", output)
        self.assertIn("性別: male", output)
        self.assertIn("国語: 68", output)
        self.assertIn("社会: 28", output)
        self.assertIn("数学: {'Math1': 66, 'Math2': 56}", output)
        self.assertIn("趣味: ['PC', 'Game']", output)
        self.assertIn("住所: ['282-2828', 'Otsu Prefecture', 'OtsuCity']", output)


if __name__ == "__main__":
    unittest.main()
