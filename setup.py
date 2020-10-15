"""setup.py for docklib"""

import pathlib

from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


def get_version(rel_path):
    """Given a path to a Python init file, return the version string."""
    with open(rel_path, "r") as openfile:
        lines = openfile.readlines()
    for line in lines:
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


setup(
    name="docklib",
    version=get_version("docklib/__init__.py"),
    description=(
        "Python module intended to assist IT "
        "administrators with manipulation of the macOS Dock."
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/homebysix/docklib",
    author="Elliot Jordan",
    author_email="elliot@elliotjordan.com",
    license="Apache 2.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: MacOS X",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    packages=["docklib"],
    include_package_data=True,
)
