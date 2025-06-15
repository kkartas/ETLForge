"""
Setup configuration for ETLTest package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="etltest",
    version="0.1.0",
    author="Kyriakos Kartas",
    author_email="mail@kkartas.gr",
    description="A Python library for generating synthetic test data and validating ETL outputs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kkartas/etltest",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "pyyaml>=5.4.0",
        "click>=8.0.0",
        "openpyxl>=3.0.0",  # For Excel support
        "numpy>=1.21.0",
    ],
    extras_require={
        "faker": ["faker>=15.0.0"],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.900",
        ],
    },
    entry_points={
        "console_scripts": [
            "etltest=etltest.cli:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 