from sysconfig import get_path
from setuptools import setup, find_packages, Extension

trth_parser = Extension(
    "mktstructure.trth_parser",
    include_dirs=[get_path("platinclude")],
    sources=["src/mktstructure/trth_parser.c"],
    language="C",
)

ext_modules = [
    trth_parser,
]

setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    ext_modules=ext_modules,
)
