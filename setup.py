#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("docs/history.rst") as history_file:
    history = history_file.read()

requirements = [
    "Click>=7.0",
    "python-dotenv>=0.20.0",
    "boto3>=1.24.17",
    "pdf2image>=1.16.0",
    "pillow>=9.1.1",
]

test_requirements = [
    "pytest>=3",
]

setup(
    author="Aldrin Navarro",
    author_email="aldrinnavarro16@gmail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="DOE Reports Extractor",
    entry_points={
        "console_scripts": [
            "doeextractor=doeextractor.cli:cli",
        ],
    },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="doeextractor",
    name="doeextractor",
    packages=find_packages(include=["doeextractor", "doeextractor.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/aldnav/doeextractor",
    version="0.1.0",
    zip_safe=False,
)
