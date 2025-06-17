"""
Unit tests for the DataGenerator class.
"""

import pytest
import pandas as pd
import tempfile
import os
from etl_forge.generator import DataGenerator
from etl_forge.exceptions import ETLForgeError


class TestDataGenerator:
    """Test cases for DataGenerator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_schema = {
            "fields": [
                {
                    "name": "id",
                    "type": "int",
                    "unique": True,
                    "nullable": False,
                    "range": {"min": 1, "max": 1000},
                },
                {
                    "name": "name",
                    "type": "string",
                    "nullable": False,
                    "length": {"min": 5, "max": 15},
                },
                {
                    "name": "score",
                    "type": "float",
                    "nullable": True,
                    "range": {"min": 0.0, "max": 100.0},
                    "precision": 2,
                    "null_rate": 0.1,
                },
                {
                    "name": "category",
                    "type": "category",
                    "nullable": False,
                    "values": ["A", "B", "C"],
                },
                {
                    "name": "date_field",
                    "type": "date",
                    "nullable": False,
                    "range": {"start": "2020-01-01", "end": "2020-12-31"},
                    "format": "%Y-%m-%d",
                },
            ]
        }

    def test_init_with_schema_dict(self):
        """Test initialization with schema dictionary."""
        generator = DataGenerator(self.test_schema)
        assert generator.schema == self.test_schema

    def test_init_empty(self):
        """Test initialization without schema."""
        generator = DataGenerator()
        assert generator.schema is None

    def test_load_schema_dict(self):
        """Test loading schema from dictionary."""
        generator = DataGenerator()
        generator.load_schema(self.test_schema)
        assert generator.schema == self.test_schema

    def test_generate_int_column(self):
        """Test integer column generation."""
        generator = DataGenerator(self.test_schema)
        field_config = self.test_schema["fields"][0]  # id field
        values = generator._generate_int_column(field_config, 100)

        assert len(values) == 100
        assert all(isinstance(v, int) for v in values)
        assert len(set(values)) == 100  # All unique
        assert all(1 <= v <= 1000 for v in values)

    def test_generate_float_column(self):
        """Test float column generation."""
        generator = DataGenerator(self.test_schema)
        field_config = self.test_schema["fields"][2]  # score field
        values = generator._generate_float_column(field_config, 100)

        assert len(values) == 100
        non_null_values = [v for v in values if v is not None]
        assert all(isinstance(v, float) for v in non_null_values)
        assert all(0.0 <= v <= 100.0 for v in non_null_values)

        # Check null rate approximately
        null_count = sum(1 for v in values if v is None)
        assert 0 <= null_count <= 20  # Should be around 10% with some variance

    def test_generate_string_column(self):
        """Test string column generation."""
        generator = DataGenerator(self.test_schema)
        field_config = self.test_schema["fields"][1]  # name field
        values = generator._generate_string_column(field_config, 50)

        assert len(values) == 50
        assert all(isinstance(v, str) for v in values)
        assert all(5 <= len(v) <= 15 for v in values)

    def test_generate_category_column(self):
        """Test categorical column generation."""
        generator = DataGenerator(self.test_schema)
        field_config = self.test_schema["fields"][3]  # category field
        values = generator._generate_category_column(field_config, 100)

        assert len(values) == 100
        assert all(v in ["A", "B", "C"] for v in values)

    def test_generate_date_column(self):
        """Test date column generation."""
        generator = DataGenerator(self.test_schema)
        field_config = self.test_schema["fields"][4]  # date_field
        values = generator._generate_date_column(field_config, 50)

        assert len(values) == 50
        assert all(isinstance(v, str) for v in values)
        # Basic date format check
        assert all(len(v) == 10 and v[4] == "-" and v[7] == "-" for v in values)

    def test_generate_data(self):
        """Test full data generation."""
        generator = DataGenerator(self.test_schema)
        df = generator.generate_data(10)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 10
        assert len(df.columns) == 5
        assert list(df.columns) == ["id", "name", "score", "category", "date_field"]

    def test_generate_data_no_schema(self):
        """Test data generation without loaded schema."""
        generator = DataGenerator()
        with pytest.raises(ETLForgeError, match="No schema loaded"):
            generator.generate_data(10)

    def test_save_data_csv(self):
        """Test saving data to CSV."""
        generator = DataGenerator(self.test_schema)
        df = generator.generate_data(5)

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = f.name

        try:
            generator.save_data(df, temp_path)
            assert os.path.exists(temp_path)

            # Verify data can be read back
            df_loaded = pd.read_csv(temp_path)
            assert len(df_loaded) == 5
            assert len(df_loaded.columns) == 5
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_generate_and_save(self):
        """Test generate and save in one step."""
        generator = DataGenerator(self.test_schema)

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = f.name

        try:
            df = generator.generate_and_save(5, temp_path)
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 5
            assert os.path.exists(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_unsupported_field_type(self):
        """Test handling of unsupported field types."""
        bad_schema = {"fields": [{"name": "bad_field", "type": "unsupported_type"}]}
        
        # Schema validation now catches this during initialization
        with pytest.raises(ETLForgeError, match="has unsupported type"):
            DataGenerator(bad_schema)


@pytest.mark.parametrize("file_format,extension", [("csv", ".csv"), ("excel", ".xlsx")])
def test_save_formats(file_format, extension):
    """Test saving data in different formats."""
    schema = {
        "fields": [{"name": "test_col", "type": "int", "range": {"min": 1, "max": 10}}]
    }
    generator = DataGenerator(schema)
    df = generator.generate_data(3)

    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as f:
        temp_path = f.name

    try:
        generator.save_data(df, temp_path, file_format)
        assert os.path.exists(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
