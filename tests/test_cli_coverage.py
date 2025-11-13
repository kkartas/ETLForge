"""
Additional CLI tests to improve coverage.
"""

import pytest
import tempfile
import os
from click.testing import CliRunner
from etl_forge.cli import cli
from etl_forge.exceptions import ETLForgeError


class TestCLIErrorHandling:
    """Test CLI error handling paths."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_generate_file_not_found(self):
        """Test generate command with non-existent schema file."""
        result = self.runner.invoke(
            cli, ["generate", "--schema", "nonexistent_schema.yaml", "--rows", "10"]
        )

        assert result.exit_code != 0
        # Click validates files before our code runs
        assert "does not exist" in result.output or "File not found" in result.output

    def test_generate_permission_error(self):
        """Test generate command with permission denied (output file)."""
        # Skip this test as it's platform-specific and hard to test reliably
        # Permission errors are better tested in manual/integration testing
        pytest.skip("Permission error testing is platform-specific")

    def test_check_verbose_with_errors(self):
        """Test check command with --verbose flag showing detailed errors."""
        schema = {
            "fields": [
                {
                    "name": "id",
                    "type": "int",
                    "unique": True,
                    "range": {"min": 1, "max": 100},
                },
                {
                    "name": "category",
                    "type": "category",
                    "values": ["A", "B", "C"],
                },
            ]
        }

        # Create schema file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as schema_file:
            import yaml

            yaml.dump(schema, schema_file)
            schema_path = schema_file.name

        # Create data file with errors
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as data_file:
            import csv

            writer = csv.writer(data_file)
            writer.writerow(["id", "category"])
            writer.writerow([1, "A"])
            writer.writerow([1, "B"])  # Duplicate ID
            writer.writerow([2, "Invalid"])  # Invalid category
            writer.writerow([999, "A"])  # Out of range
            data_path = data_file.name

        try:
            result = self.runner.invoke(
                cli, ["check", "--input", data_path, "--schema", schema_path, "--verbose"]
            )

            # Should show detailed errors
            assert "Detailed Errors" in result.output
            assert "duplicate" in result.output.lower() or "unique" in result.output.lower()
            assert result.exit_code == 1  # Should fail validation
        finally:
            os.unlink(schema_path)
            os.unlink(data_path)

    def test_check_many_errors_truncation(self):
        """Test check command truncates after 20 errors."""
        schema = {
            "fields": [
                {
                    "name": "id",
                    "type": "int",
                    "range": {"min": 1, "max": 10},
                }
            ]
        }

        # Create schema file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as schema_file:
            import yaml

            yaml.dump(schema, schema_file)
            schema_path = schema_file.name

        # Create data file with many errors (>20)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as data_file:
            import csv

            writer = csv.writer(data_file)
            writer.writerow(["id"])
            # Add 30 rows with out-of-range values
            for i in range(30):
                writer.writerow([100 + i])  # All out of range
            data_path = data_file.name

        try:
            result = self.runner.invoke(
                cli, ["check", "--input", data_path, "--schema", schema_path, "--verbose"]
            )

            # Should show truncation message
            assert "and" in result.output and "more errors" in result.output
            assert result.exit_code == 1
        finally:
            os.unlink(schema_path)
            os.unlink(data_path)

    def test_check_file_not_found(self):
        """Test check command with non-existent data file."""
        schema = {"fields": [{"name": "id", "type": "int"}]}

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as schema_file:
            import yaml

            yaml.dump(schema, schema_file)
            schema_path = schema_file.name

        try:
            result = self.runner.invoke(
                cli,
                [
                    "check",
                    "--input",
                    "nonexistent_data.csv",
                    "--schema",
                    schema_path,
                ],
            )

            assert result.exit_code != 0
            # Click validates files before our code runs
            assert "does not exist" in result.output or "File not found" in result.output
        finally:
            os.unlink(schema_path)

