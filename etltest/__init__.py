"""
ETLTest - A Python library for generating test data and validating ETL outputs.
"""

__version__ = "1.0.0"

class ETLTestError(Exception):
    """Base exception for all ETLTest errors."""
    pass

from .generator import DataGenerator
from .validator import DataValidator

__all__ = ["DataGenerator", "DataValidator", "ETLTestError"] 