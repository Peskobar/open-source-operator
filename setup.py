from setuptools import setup, find_packages

setup(
    name="openoperator",
    version="0.1.0",
    packages=find_packages(),
    py_modules=["cli"],
    entry_points={"console_scripts": ["oss-op=cli:main"]},
)
