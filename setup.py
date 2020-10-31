#!/usr/bin/env python
from setuptools import setup

setup(
    name="tap-bls",
    version="0.1.0",
    description="Singer.io tap for extracting data from the Bureau of Labor Statistics API 2.0",
    author="Stitch + Fraser Marlow",
    url="http://singer.io",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["tap_bls"],
    install_requires=[
        # NB: Pin these to a more specific version for tap reliability
        "singer-python==5.9.0",
        "singer-tools==0.4.1",
        "requests==2.20.0"
    ],
    entry_points="""
    [console_scripts]
    tap-bls=tap_bls:main
    """,
    packages=["tap_bls"],
    package_data = {
        "schemas": ["tap_bls/schemas/*.json"]
    },
    include_package_data=True,
)
