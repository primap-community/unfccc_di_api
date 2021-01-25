#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("CHANGELOG.rst") as history_file:
    history = history_file.read()

requirements = [
    "pandas",
    "treelib",
    "requests",
]

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "pytest>=3",
]

setup(
    author="Mika Pflüger",
    author_email="mika.pflueger@pik-potsdam.de",
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Python wrapper around the Flexible Query API of the UNFCCC.",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="unfccc_di_api",
    name="unfccc_di_api",
    packages=find_packages(include=["unfccc_di_api", "unfccc_di_api.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/pik-primap/unfccc_di_api",
    version="1.1.0",
    zip_safe=False,
)
