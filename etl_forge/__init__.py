"""
ETLForge - A Python library for generating test data and validating ETL
outputs.
"""

from .generator import DataGenerator
from .validator import DataValidator
from .exceptions import ETLForgeError

__version__ = "1.0.3"

__all__ = ["DataGenerator", "DataValidator", "ETLForgeError"]
