import shutil
import unittest
from datetime import timedelta
from pathlib import Path
from typing import Any

from otsuvalidator import CBool, CFloat, CInt, CPath, CString, CTimedelta


class Settings:
    pd_setting = CPath(must_exist=True, path_type=Path.is_dir)
    pf_setting = CPath(".cfg", "json", must_exist=False, path_type=lambda x: Path.is_file(x))
    profile_name = CString(1, 30)
    save_span = CTimedelta()
    enable_beep = CBool(("sushi",))
    beep_frequency = CInt(37, 32767)
    beep_duration_seconds = CFloat(0.0, 5.0)
    # "type: ignore"を使わずに`a.private=0`を`int`型として解析されたくない場合は以下のようにする
    _private = CString(1, 10)

    @property
    def private(self) -> str:
        return self._private

    @private.setter
    def private(self, value: Any) -> None:
        self._private = value


def reset_sample() -> None:
    pd = Path("./tmp_settings")
    if not pd.exists():
        return
    if pd.is_file():
        pd.unlink()
    else:
        shutil.rmtree(pd)


class TestSettingsConverters(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg = Settings()
        reset_sample()

    def test_pd_setting(self) -> None:
        """pd_setting属性の検証"""
        reset_sample()
        pd = "./tmp_settings"
        # must_existにより存在確認が行われる
        with self.assertRaisesRegex(FileNotFoundError, "のパスは存在しません"):
            self.cfg.pd_setting = pd
        # 同名のファイルを生成
        Path(pd).touch()
        with self.assertRaisesRegex(ValueError, "パス種別検証に失敗しました"):
            self.cfg.pd_setting = pd
        reset_sample()
        # 同名のフォルダを作成
        Path(pd).mkdir()
        self.cfg.pd_setting = pd
        self.assertEqual(self.cfg.pd_setting, Path(pd))

    def test_pf_setting(self) -> None:
        """pf_setting属性の検証"""
        reset_sample()
        pf = "./tmp_settings/settings"
        with self.assertRaisesRegex(ValueError, "いずれかである必要があります"):
            self.cfg.pf_setting = f"{pf}.txt"
        pf = f"{pf}.cfg"
        # ファイル名のフォルダを作成する
        p_pf = Path(pf)
        p_pf.mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "パス種別検証に失敗しました"):
            self.cfg.pf_setting = pf
        # フォルダを削除し、ファイルを作成する
        shutil.rmtree(p_pf)
        p_pf.parent.mkdir(parents=True, exist_ok=True)
        p_pf.touch()
        self.cfg.pf_setting = pf
        self.assertEqual(self.cfg.pf_setting, p_pf)
        reset_sample()

    def test_profile_name(self) -> None:
        """profile_name属性の検証"""
        with self.assertRaisesRegex(ValueError, "長さは`30以下`である必要があります"):
            # 2535301200456458802993406410752
            self.cfg.profile_name = 2 << 100
        with self.assertRaisesRegex(ValueError, "長さは`1以上`である必要があります"):
            self.cfg.profile_name = ""
        self.cfg.profile_name = 28
        self.assertEqual(self.cfg.profile_name, "28")

    def test_save_span(self) -> None:
        """save_span属性の検証"""
        delta = timedelta(1, 2, 3, 4, 5, 6, 7)
        self.cfg.save_span = "50 days, 6:05:02.004003"
        self.assertEqual(self.cfg.save_span, delta)

        delta = timedelta(hours=1, minutes=2)
        self.cfg.save_span = "1:2:0"
        self.assertEqual(self.cfg.save_span, delta)

        delta = timedelta(days=1)
        self.cfg.save_span = {"days": 1}
        self.assertEqual(self.cfg.save_span, delta)

        with self.assertRaisesRegex(TypeError, "`timedelta型`に変換可能な値である必要があります"):
            self.cfg.save_span = {"day": 1}

        delta = timedelta(1, 2, 3, 4)
        self.cfg.save_span = [1, 2, 3, 4]
        self.assertEqual(self.cfg.save_span, delta)

        with self.assertRaisesRegex(TypeError, "`timedelta型`に変換可能な値である必要があります"):
            self.cfg.save_span = [1, 2, 3, 4, 5, 6, 7, 8]

    def test_enable_beep(self) -> None:
        """enable_beep属性の検証"""
        self.cfg.enable_beep = "YeS"
        self.assertEqual(self.cfg.enable_beep, True)
        with self.assertRaisesRegex(ValueError, "クラス定義の検証に失敗しました。"):
            self.cfg.enable_beep = "Ye"
        self.cfg.enable_beep = 1
        self.assertEqual(self.cfg.enable_beep, True)
        self.cfg.enable_beep = 0.0
        self.assertEqual(self.cfg.enable_beep, False)
        self.cfg.enable_beep = "1.0"
        self.assertEqual(self.cfg.enable_beep, True)
        self.cfg.enable_beep = "sushi"
        self.assertEqual(self.cfg.enable_beep, True)

    def test_beep_frequency(self) -> None:
        """beep_frequency属性の検証"""
        with self.assertRaisesRegex(ValueError, "`37以上`である必要があります"):
            self.cfg.beep_frequency = 36
        with self.assertRaisesRegex(ValueError, "`int型`に変換できませんでした"):
            self.cfg.beep_frequency = 37.00000000000001
        self.cfg.beep_frequency = 37.000000000000001
        self.assertEqual(self.cfg.beep_frequency, 37)
        self.cfg.beep_frequency = "37.000000000000001"
        self.assertEqual(self.cfg.beep_frequency, 37)
        self.cfg.beep_frequency = "37"
        self.assertEqual(self.cfg.beep_frequency, 37)
        with self.assertRaisesRegex(ValueError, "`32767以下`である必要があります"):
            self.cfg.beep_frequency = 32768

    def test_beep_duration_seconds(self) -> None:
        with self.assertRaisesRegex(ValueError, r"`0\.0以上`である必要があります"):
            self.cfg.beep_duration_seconds = -1.0
        with self.assertRaisesRegex(ValueError, r"`5\.0以下`である必要があります"):
            self.cfg.beep_duration_seconds = 5.1
        self.cfg.beep_duration_seconds = "5.0"
        self.assertEqual(self.cfg.beep_duration_seconds, 5.0)
        self.cfg.beep_duration_seconds = 3
        self.assertEqual(self.cfg.beep_duration_seconds, 3.0)

    def test_private(self) -> None:
        """_private属性のテスト"""
        self.cfg.private = 26
        self.assertEqual(self.cfg.private, "26")

        class A(Settings):
            pass

        a = A()
        a.private = 26
        self.assertEqual(a.private, "26")


if __name__ == "__main__":
    unittest.main()
