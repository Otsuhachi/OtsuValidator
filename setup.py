from setuptools import find_packages, setup

__VERSION__ = "2.0.1"

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()
with open("LICENSE.txt", "r", encoding="utf-8") as f:
    lcs = f.read()

setup(
    name="otsuvalidator",
    version=__VERSION__,
    url="https://github.com/Otsuhachi/OtsuValidator",
    description="単体でもディスクリプタとしても使用できるバリデータライブラリ",
    long_description_content_type="text/markdown",
    long_description=readme,
    author="Otsuhachi",
    author_email="agequodagis.tufuiegoeris@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    license=lcs,
    keywords="Python validator descriptor converter",
    python_requires=">=3.8",
)
