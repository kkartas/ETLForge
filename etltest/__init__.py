"""
ETLTest - A Python library for generating test data and validating ETL outputs.
"""

__version__ = "0.1.0"

from .generator import DataGenerator
from .validator import DataValidator

__all__ = ["DataGenerator", "DataValidator"] 