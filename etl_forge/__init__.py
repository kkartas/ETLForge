"""
ETLForge - A Python library for generating test data and validating ETL
outputs.
"""

from .generator import DataGenerator
from .validator import DataValidator
from .exceptions import ETLForgeError
from .schema_adapter import SchemaAdapter, FrictionlessAdapter, JsonSchemaAdapter

__version__ = "1.1.1"

__all__ = [
    "DataGenerator",
    "DataValidator",
    "ETLForgeError",
    "SchemaAdapter",
    "FrictionlessAdapter",
    "JsonSchemaAdapter",
]
