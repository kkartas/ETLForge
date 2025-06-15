"""
Tests for error handling and failure cases in ETLTest.
"""

import pytest
import tempfile
import os
import pandas as pd
from etltest.generator import DataGenerator
from etltest.validator import DataValidator
from etltest import ETLTestError


def test_generator_load_nonexistent_schema():
    """Test that DataGenerator raises ETLTestError for a missing schema file."""
    with pytest.raises(ETLTestError, match="Schema file not found"):
        DataGenerator("nonexistent_schema.yaml")

def test_generator_load_unsupported_format():
    """Test that DataGenerator raises ETLTestError for an unsupported schema format."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write(b"test")
        temp_path = f.name
    
    with pytest.raises(ETLTestError, match="Unsupported schema file format"):
        DataGenerator(temp_path)
    
    os.unlink(temp_path)

def test_generator_unique_constraint_impossible():
    """Test that DataGenerator raises ETLTestError when unique constraint cannot be met."""
    schema = {
        'fields': [{'name': 'id', 'type': 'int', 'unique': True, 'range': {'min': 1, 'max': 5}}]
    }
    generator = DataGenerator(schema)
    with pytest.raises(ETLTestError, match="Cannot generate 10 unique integers"):
        generator.generate_data(10)

def test_validator_load_nonexistent_data():
    """Test that DataValidator raises ETLTestError for a missing data file."""
    validator = DataValidator({'fields': []})
    with pytest.raises(ETLTestError, match="Data file not found"):
        validator.load_data("nonexistent_data.csv")

def test_validator_without_schema():
    """Test that DataValidator methods raise ETLTestError if no schema is loaded."""
    validator = DataValidator()
    with pytest.raises(ETLTestError, match="No schema loaded"):
        validator.validate(pd.DataFrame())

def test_cli_generate_handles_error(runner):
    """Test that the CLI 'generate' command shows a clean error message."""
    result = runner.invoke(
        ['generate', '--schema', 'nonexistent.yaml', '--rows', '10', '--output', 'out.csv']
    )
    assert result.exit_code != 0
    assert "Error: Schema file not found" in result.output

def test_cli_check_handles_error(runner):
    """Test that the CLI 'check' command shows a clean error message."""
    # Create a dummy schema file to pass the first check
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("fields:\n  - {name: id, type: int}")
        schema_path = f.name

    result = runner.invoke(
        ['check', '--input', 'nonexistent.csv', '--schema', schema_path]
    )
    assert result.exit_code != 0
    assert "Error: Data file not found" in result.output
    
    os.unlink(schema_path) 