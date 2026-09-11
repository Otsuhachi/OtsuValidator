import re
from pathlib import Path

from setuptools import find_packages, setup

pd_this = Path(__file__).parent

with (pd_this / "README.md").open("r", encoding="utf-8") as f:
    readme = f.read()

with (pd_this / "LICENSE.txt").open("r", encoding="utf-8") as f:
    lcs = f.read()

with (pd_this / "otsuvalidator/__init__.py").open("r", encoding="utf-8") as f:
    for line in (l.rstrip() for l in f):
        if (find := re.fullmatch(r'__VERSION__ = "([^"]+)"', line)) is None:
            continue
        __VERSION__ = find.groups()[0]
        break
    else:
        msg = "`otsuvalidator`のバージョン情報を取得できませんでした。"
        raise ValueError(msg)


setup(
    name="otsuvalidator",
    version=__VERSION__,
    url="https://github.com/Otsuhachi/OtsuValidator",
    description="単体でもディスクリプタとしても使用できるバリデータライブラリ",
    long_description_content_type="text/markdown",
    long_description=readme,
    author="Otsuhachi",
    author_email="agequodagis.tufuiegoeris@gmail.com",
    packages=find_packages(where=".", include=["otsuvalidator*"]),
    package_data={"otsuvalidator": ["py.typed"]},
    include_package_data=True,
    license=lcs,
    keywords="Python validator descriptor converter",
    python_requires=">=3.12",
)
