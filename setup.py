"""Set up the Python API for dingz devices."""
import os

import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.rst"), encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name="python-dingz",
    version="0.4.0",
    description="Python API for interacting with Dingz devices",
    long_description=long_description,
    url="https://github.com/home-assistant-ecosystem/python-dingz",
    author="Fabian Affolter",
    author_email="fabian@affolter-engineering.ch",
    license="Apache License 2.0",
    install_requires=["aiohttp<4", "async_timeout<5", "click", "setuptools"],
    packages=find_packages(),
    python_requires='>=3.8',
    zip_safe=True,
    include_package_data=True,
    entry_points={"console_scripts": ["dingz = dingz.cli:main"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Utilities",
    ],
)
