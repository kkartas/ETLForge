"""
Tests for error handling and failure cases in ETLForge.
"""

import pytest
import tempfile
import os
import pandas as pd
from etl_forge.generator import DataGenerator
from etl_forge.validator import DataValidator
from etl_forge.exceptions import ETLForgeError
from etl_forge.cli import cli


def test_generator_load_nonexistent_schema():
    """Test that DataGenerator raises ETLForgeError for a missing schema file."""
    with pytest.raises(ETLForgeError, match="Schema file not found"):
        DataGenerator("nonexistent_schema.yaml")


def test_generator_load_unsupported_format():
    """Test that DataGenerator raises ETLForgeError for an unsupported schema format."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write(b"test")
        temp_path = f.name

    with pytest.raises(ETLForgeError, match="Unsupported schema file format"):
        DataGenerator(temp_path)

    os.unlink(temp_path)


def test_generator_unique_constraint_impossible():
    """Test that DataGenerator raises ETLForgeError when unique constraint cannot be met."""
    schema = {
        "fields": [
            {"name": "id", "type": "int", "unique": True, "range": {"min": 1, "max": 5}}
        ]
    }
    generator = DataGenerator(schema)
    with pytest.raises(ETLForgeError, match="Cannot generate 10 unique integers"):
        generator.generate_data(10)


def test_validator_invalid_input_type():
    """Test that DataValidator raises ETLForgeError for non-DataFrame input."""
    validator = DataValidator({"fields": [{"name": "id", "type": "int"}]})
    with pytest.raises(ETLForgeError, match="Expected pandas DataFrame"):
        validator.validate("not a dataframe")


def test_validator_without_schema():
    """Test that DataValidator methods raise ETLForgeError if no schema is loaded."""
    validator = DataValidator()
    with pytest.raises(ETLForgeError, match="No schema loaded"):
        validator.validate(pd.DataFrame())


def test_cli_generate_handles_error(runner):
    """Test that the CLI 'generate' command shows a clean error message."""
    result = runner.invoke(
        cli,
        [
            "generate",
            "--schema",
            "nonexistent.yaml",
            "--rows",
            "10",
            "--output",
            "out.csv",
        ],
    )
    assert result.exit_code != 0
    assert "Path 'nonexistent.yaml' does not exist" in result.output


def test_cli_check_handles_error(runner):
    """Test that the CLI 'check' command shows a clean error message."""
    # Create a dummy schema file to pass the first check
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("fields:\n  - {name: id, type: int}")
        schema_path = f.name

    result = runner.invoke(
        cli, ["check", "--input", "nonexistent.csv", "--schema", schema_path]
    )
    assert result.exit_code != 0
    assert "Path 'nonexistent.csv' does not exist" in result.output

    os.unlink(schema_path)
