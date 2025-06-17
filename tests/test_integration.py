"""
Integration tests for ETLForge CLI commands.
"""

import os
import tempfile
import pandas as pd
import pytest
from click.testing import CliRunner
from etl_forge.cli import cli


class TestCLIIntegration:
    """Integration tests for CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
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
                    "name": "category",
                    "type": "category",
                    "nullable": False,
                    "values": ["A", "B", "C"],
                },
            ]
        }

    def test_cli_generate_command(self):
        """Test the generate command with real files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create schema file
            schema_path = os.path.join(temp_dir, "test_schema.yaml")
            with open(schema_path, "w") as f:
                import yaml
                yaml.dump(self.test_schema, f)

            # Create output path
            output_path = os.path.join(temp_dir, "test_output.csv")

            # Run generate command
            result = self.runner.invoke(
                cli,
                [
                    "generate",
                    "--schema", schema_path,
                    "--rows", "10",
                    "--output", output_path,
                ]
            )

            # Check command succeeded
            assert result.exit_code == 0
            assert "Successfully generated 10 rows" in result.output

            # Verify output file exists and has correct structure
            assert os.path.exists(output_path)
            df = pd.read_csv(output_path)
            assert len(df) == 10
            assert list(df.columns) == ["id", "name", "category"]

    def test_cli_check_command_valid_data(self):
        """Test the check command with valid data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create schema file
            schema_path = os.path.join(temp_dir, "test_schema.yaml")
            with open(schema_path, "w") as f:
                import yaml
                yaml.dump(self.test_schema, f)

            # Create valid test data
            data_path = os.path.join(temp_dir, "test_data.csv")
            test_data = pd.DataFrame({
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "category": ["A", "B", "C"]
            })
            test_data.to_csv(data_path, index=False)

            # Run check command
            result = self.runner.invoke(
                cli,
                [
                    "check",
                    "--input", data_path,
                    "--schema", schema_path,
                ]
            )

            # Check command succeeded
            assert result.exit_code == 0
            assert "Validation PASSED" in result.output

    def test_cli_check_command_invalid_data(self):
        """Test the check command with invalid data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create schema file
            schema_path = os.path.join(temp_dir, "test_schema.yaml")
            with open(schema_path, "w") as f:
                import yaml
                yaml.dump(self.test_schema, f)

            # Create invalid test data (missing column)
            data_path = os.path.join(temp_dir, "test_data.csv")
            test_data = pd.DataFrame({
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                # Missing 'category' column
            })
            test_data.to_csv(data_path, index=False)

            # Run check command
            result = self.runner.invoke(
                cli,
                [
                    "check",
                    "--input", data_path,
                    "--schema", schema_path,
                ]
            )

            # Check command failed with correct exit code
            assert result.exit_code == 1
            assert "Validation FAILED" in result.output

    def test_cli_check_command_with_report(self):
        """Test the check command with report generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create schema file
            schema_path = os.path.join(temp_dir, "test_schema.yaml")
            with open(schema_path, "w") as f:
                import yaml
                yaml.dump(self.test_schema, f)

            # Create invalid test data
            data_path = os.path.join(temp_dir, "test_data.csv")
            test_data = pd.DataFrame({
                "id": [1, 2, "invalid"],  # Invalid type in id column
                "name": ["Alice", "Bob", "Charlie"],
                "category": ["A", "B", "D"]  # Invalid category
            })
            test_data.to_csv(data_path, index=False)

            # Report path
            report_path = os.path.join(temp_dir, "invalid_rows.csv")

            # Run check command with report
            result = self.runner.invoke(
                cli,
                [
                    "check",
                    "--input", data_path,
                    "--schema", schema_path,
                    "--report", report_path,
                ]
            )

            # Check command failed
            assert result.exit_code == 1
            assert "Invalid rows report saved to" in result.output

            # Verify report file was created
            assert os.path.exists(report_path)

    def test_cli_create_schema_command(self):
        """Test the create-schema command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            schema_path = os.path.join(temp_dir, "example_schema.yaml")

            # Run create-schema command
            result = self.runner.invoke(
                cli,
                ["create-schema", schema_path]
            )

            # Check command succeeded
            assert result.exit_code == 0
            assert "Example schema created" in result.output

            # Verify schema file was created and is valid
            assert os.path.exists(schema_path)
            
            # Test that the created schema can be loaded
            from etl_forge import DataGenerator
            generator = DataGenerator(schema_path)
            assert generator.schema is not None
            assert "fields" in generator.schema

    def test_cli_version(self):
        """Test the version command."""
        result = self.runner.invoke(cli, ["--version"])
        
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_cli_help(self):
        """Test the help command."""
        result = self.runner.invoke(cli, ["--help"])
        
        assert result.exit_code == 0
        assert "ETLForge" in result.output
        assert "generate" in result.output
        assert "check" in result.output

    def test_cli_generate_with_excel_output(self):
        """Test generate command with Excel output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create schema file
            schema_path = os.path.join(temp_dir, "test_schema.yaml")
            with open(schema_path, "w") as f:
                import yaml
                yaml.dump(self.test_schema, f)

            # Create output path with .xlsx extension
            output_path = os.path.join(temp_dir, "test_output.xlsx")

            # Run generate command
            result = self.runner.invoke(
                cli,
                [
                    "generate",
                    "--schema", schema_path,
                    "--rows", "5",
                    "--output", output_path,
                    "--format", "excel"
                ]
            )

            # Check command succeeded
            assert result.exit_code == 0
            assert "Successfully generated 5 rows" in result.output

            # Verify output file exists and has correct structure
            assert os.path.exists(output_path)
            df = pd.read_excel(output_path)
            assert len(df) == 5
            assert list(df.columns) == ["id", "name", "category"]

    def test_cli_error_handling_missing_schema(self):
        """Test CLI error handling for missing schema file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent_schema = os.path.join(temp_dir, "nonexistent.yaml")
            output_path = os.path.join(temp_dir, "output.csv")

            result = self.runner.invoke(
                cli,
                [
                    "generate",
                    "--schema", nonexistent_schema,
                    "--rows", "10",
                    "--output", output_path,
                ]
            )

            assert result.exit_code != 0
            assert "Error:" in result.output

    def test_cli_error_handling_invalid_schema(self):
        """Test CLI error handling for invalid schema."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid schema file
            schema_path = os.path.join(temp_dir, "invalid_schema.yaml")
            with open(schema_path, "w") as f:
                f.write("invalid: yaml: content: [unclosed")

            output_path = os.path.join(temp_dir, "output.csv")

            result = self.runner.invoke(
                cli,
                [
                    "generate",
                    "--schema", schema_path,
                    "--rows", "10",
                    "--output", output_path,
                ]
            )

            assert result.exit_code != 0
            assert "Error:" in result.output 