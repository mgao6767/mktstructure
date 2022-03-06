from setuptools import setup, find_packages, Extension


requires = ["requests"]

trth_parser = Extension(
    "mktstructure.trth_parser",
    sources=["mktstructure/trth_parser.c"],
)

setup(
    name="mktstructure",
    packages=find_packages(),
    install_requires=requires,
    entry_points={"console_scripts": ["mktstructure=mktstructure.main:main"]},
    ext_modules=[trth_parser],
)
