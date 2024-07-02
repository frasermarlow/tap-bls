#!/usr/bin/env python
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="tap-bls",
    version="0.2.0",
    description="Singer.io tap for extracting data from the Bureau of Labor Statistics API 2.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Stitch + Fraser Marlow",
    author_email="tap.bls@frasermarlow.com",
    url="https://github.com/frasermarlow/tap-bls",
    classifiers=["Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"],
    py_modules=["tap_bls"],
    install_requires=[
        "singer-python==5.9.0","singer-tools==0.4.1",
        "requests==2.32.2","backoff==1.8.0",
        "jsonschema==2.6.0","pylint==1.8.3",
        "pytz==2018.4","pytzdata==2020.1",
        "requests==2.32.2","simplejson==3.11.1",
        "singer-encodings==0.0.3","singer-python==5.9.0","singer-tools==0.4.1",
        "python-dateutil==2.8.2"
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
    python_requires='>=3.5'
)
