"""
Data validator module for validating CSV/Excel files against schema definitions.
"""

import pandas as pd
import numpy as np
import yaml
import json
from datetime import datetime
from typing import Dict, Any, Union
from pathlib import Path
from .exceptions import ETLForgeError


class ValidationResult:
    """Container for validation results."""

    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.invalid_rows = []
        self.summary = {
            "total_rows": 0,
            "valid_rows": 0,
            "invalid_rows": 0,
            "columns_checked": 0,
            "missing_columns": [],
            "extra_columns": [],
        }

    def add_error(
        self, error_type: str, column: str, row_idx: int = None, message: str = None
    ):
        """Add a validation error."""
        self.is_valid = False
        error = {
            "type": error_type,
            "column": column,
            "row": row_idx,
            "message": message,
        }
        self.errors.append(error)

        if row_idx is not None and row_idx not in self.invalid_rows:
            self.invalid_rows.append(row_idx)


class DataValidator:
    """
    Validates tabular data against a declarative schema.

    This class reads a schema and a data file (CSV or Excel), and then
    performs a series of validation checks to ensure the data conforms to the
    schema's specifications.
    """

    def __init__(self, schema_path: Union[str, Path, dict] = None):
        """
        Initializes the DataValidator.

        Args:
            schema_path: The path to a YAML/JSON schema file or a dictionary
                containing the schema definition.

        Raises:
            ETLForgeError: If the schema file cannot be found or parsed.
        """
        self.schema: Dict[str, Any] = None

        if schema_path:
            self.load_schema(schema_path)

    def load_schema(self, schema_path: Union[str, Path, dict]):
        """
        Loads a schema from a file path or a dictionary.

        Args:
            schema_path: The path to a YAML/JSON schema file or a dictionary
                containing the schema definition.

        Raises:
            ETLForgeError: If the schema file is not found, has an unsupported
                format, or cannot be parsed.
        """
        if isinstance(schema_path, dict):
            self.schema = schema_path
            return

        schema_path_obj = Path(schema_path)
        if not schema_path_obj.exists():
            raise ETLForgeError(f"Schema file not found at: {schema_path}")

        suffix = schema_path_obj.suffix.lower()
        try:
            with open(schema_path_obj, "r", encoding="utf-8") as file:
                if suffix in [".yaml", ".yml"]:
                    self.schema = yaml.safe_load(file) or {}
                elif suffix == ".json":
                    self.schema = json.load(file) or {}
                else:
                    raise ETLForgeError(f"Unsupported schema file format: {suffix}")
        except (IOError, yaml.YAMLError, json.JSONDecodeError) as e:
            raise ETLForgeError(f"Failed to load or parse schema file: {e}") from e

    def load_data(self, data_path: Union[str, Path]) -> pd.DataFrame:
        """
        Loads data from a CSV or Excel file into a pandas DataFrame.

        Args:
            data_path: The path to the data file.

        Returns:
            A pandas DataFrame containing the loaded data.

        Raises:
            ETLForgeError: If the data file is not found, has an unsupported
                format, or cannot be parsed by pandas.
        """
        data_path_obj = Path(data_path)
        if not data_path_obj.exists():
            raise ETLForgeError(f"Data file not found at: {data_path}")

        suffix = data_path_obj.suffix.lower()
        try:
            if suffix == ".csv":
                return pd.read_csv(data_path_obj)
            elif suffix in [".xlsx", ".xls"]:
                return pd.read_excel(data_path_obj)
            else:
                raise ETLForgeError(f"Unsupported data file format: {suffix}")
        except (IOError, PermissionError, ValueError) as e:
            raise ETLForgeError(f"Failed to load data from {data_path}: {e}") from e

    def _validate_column_existence(self, df: pd.DataFrame, result: ValidationResult):
        """Validate that all required columns exist."""
        expected_columns = {field["name"] for field in self.schema.get("fields", [])}
        actual_columns = set(df.columns)

        missing_columns = expected_columns - actual_columns
        extra_columns = actual_columns - expected_columns

        result.summary["missing_columns"] = list(missing_columns)
        result.summary["extra_columns"] = list(extra_columns)

        for col in missing_columns:
            result.add_error(
                "missing_column",
                col,
                message=f"Column '{col}' is missing from the data",
            )

    def _validate_data_types(self, df: pd.DataFrame, result: ValidationResult):
        """Validate data types for each column."""
        for field in self.schema.get("fields", []):
            field_name = field["name"]
            field_type = field["type"].lower()

            if field_name not in df.columns:
                continue  # Already handled in column existence validation

            column_data = df[field_name]

            # Skip null values for type checking unless nullable is False
            non_null_data = column_data.dropna()

            if field_type == "int":
                invalid_mask = ~non_null_data.apply(
                    lambda x: isinstance(x, (int, np.integer))
                    or (isinstance(x, (float, np.floating)) and x.is_integer())
                )
            elif field_type == "float":
                invalid_mask = ~non_null_data.apply(
                    lambda x: isinstance(x, (int, float, np.number))
                )
            elif field_type == "string":
                invalid_mask = ~non_null_data.apply(lambda x: isinstance(x, str))
            elif field_type == "date":
                date_format = field.get("format", "%Y-%m-%d")
                invalid_mask = ~non_null_data.apply(
                    lambda x: self._is_valid_date(x, date_format)
                )
            elif field_type == "category":
                valid_values = field.get("values", [])
                invalid_mask = ~non_null_data.isin(valid_values)
            else:
                continue

            # Add errors for invalid types
            invalid_indices = non_null_data[invalid_mask].index
            for idx in invalid_indices:
                result.add_error(
                    "invalid_type",
                    field_name,
                    idx,
                    f"Value '{df.loc[idx, field_name]}' is not of type '{field_type}'",
                )

    def _is_valid_date(self, value: Any, date_format: str) -> bool:
        """Check if a value is a valid date in the specified format."""
        if not isinstance(value, str):
            return False
        try:
            datetime.strptime(value, date_format)
            return True
        except ValueError:
            return False

    def _validate_constraints(self, df: pd.DataFrame, result: ValidationResult):
        """Validate field constraints."""
        for field in self.schema.get("fields", []):
            field_name = field["name"]

            if field_name not in df.columns:
                continue

            column_data = df[field_name]

            # Check nullable constraint
            if not field.get("nullable", False):
                null_mask = column_data.isnull()
                null_indices = df[null_mask].index
                for idx in null_indices:
                    result.add_error(
                        "null_value",
                        field_name,
                        idx,
                        f"Null value found in non-nullable column '{field_name}'",
                    )

            # Check unique constraint
            if field.get("unique", False):
                duplicated_mask = (
                    column_data.duplicated(keep=False) & column_data.notnull()
                )
                duplicate_indices = df[duplicated_mask].index
                for idx in duplicate_indices:
                    result.add_error(
                        "duplicate_value",
                        field_name,
                        idx,
                        f"Duplicate value '{df.loc[idx, field_name]}' in unique column '{field_name}'",
                    )

            # Check range constraints (only for valid numeric types)
            if "range" in field and field["type"].lower() in ["int", "float"]:
                range_config = field["range"]
                min_val = range_config.get("min")
                max_val = range_config.get("max")

                # Only check ranges for valid numeric values
                if field["type"].lower() == "int":
                    valid_numeric_mask = column_data.apply(
                        lambda x: isinstance(x, (int, np.integer)) or 
                        (isinstance(x, (float, np.floating)) and x.is_integer())
                    ) & column_data.notnull()
                else:  # float
                    valid_numeric_mask = column_data.apply(
                        lambda x: isinstance(x, (int, float, np.number))
                    ) & column_data.notnull()

                valid_numeric_data = column_data[valid_numeric_mask]

                if min_val is not None:
                    below_min_mask = valid_numeric_data < min_val
                    below_min_indices = valid_numeric_data[below_min_mask].index
                    for idx in below_min_indices:
                        result.add_error(
                            "range_violation",
                            field_name,
                            idx,
                            f"Value '{df.loc[idx, field_name]}' is below minimum {min_val}",
                        )

                if max_val is not None:
                    above_max_mask = valid_numeric_data > max_val
                    above_max_indices = valid_numeric_data[above_max_mask].index
                    for idx in above_max_indices:
                        result.add_error(
                            "range_violation",
                            field_name,
                            idx,
                            f"Value '{df.loc[idx, field_name]}' is above maximum {max_val}",
                        )

            # Check categorical values
            if field["type"].lower() == "category" and "values" in field:
                valid_values = field["values"]
                invalid_mask = (~column_data.isin(valid_values)) & column_data.notnull()
                invalid_indices = df[invalid_mask].index
                for idx in invalid_indices:
                    result.add_error(
                        "invalid_category",
                        field_name,
                        idx,
                        f"Value '{df.loc[idx, field_name]}' is not in allowed categories {valid_values}",
                    )

    def validate(self, data_path: Union[str, Path, pd.DataFrame]) -> ValidationResult:
        """
        Validates data against the loaded schema.

        This is the main validation method. It loads the data (if a path is
        provided) and runs all configured validation checks.

        Args:
            data_path: The path to the data file (CSV/Excel) or a pandas
                DataFrame that is already loaded.

        Returns:
            A `ValidationResult` object containing the detailed results of
            the validation run.

        Raises:
            ETLForgeError: If no schema has been loaded.
        """
        if not self.schema:
            raise ETLForgeError("No schema loaded. Use load_schema() first.")

        if isinstance(data_path, pd.DataFrame):
            df = data_path
        else:
            df = self.load_data(data_path)

        result = ValidationResult()
        result.summary["total_rows"] = len(df)
        result.summary["columns_checked"] = len(self.schema.get("fields", []))

        # Run all validation checks
        self._validate_column_existence(df, result)
        self._validate_data_types(df, result)
        self._validate_constraints(df, result)

        # Update summary
        result.summary["invalid_rows"] = len(set(result.invalid_rows))
        result.summary["valid_rows"] = (
            result.summary["total_rows"] - result.summary["invalid_rows"]
        )

        return result

    def validate_and_report(
        self,
        data_path: Union[str, Path, pd.DataFrame],
        report_path: Union[str, Path] = None,
    ) -> ValidationResult:
        """
        Validates data and optionally saves a report of invalid rows.

        Args:
            data_path: The path to the data file (CSV/Excel) or a pandas
                DataFrame that is already loaded.
            report_path: The destination file path for the invalid rows report.
                If None, no report is saved.

        Returns:
            A `ValidationResult` object containing the detailed results.

        Raises:
            ETLForgeError: If an error occurs while writing the report file.
        """
        result = self.validate(data_path)

        if report_path and result.invalid_rows:
            if isinstance(data_path, pd.DataFrame):
                df = data_path
            else:
                df = self.load_data(data_path)

            # Create report DataFrame with invalid rows and error details
            invalid_df = df.loc[result.invalid_rows].copy()

            # Add error details
            error_details = []
            for idx in invalid_df.index:
                row_errors = [error for error in result.errors if error["row"] == idx]
                error_messages = [
                    f"{error['type']}: {error['message']}" for error in row_errors
                ]
                error_details.append("; ".join(error_messages))

            invalid_df["validation_errors"] = error_details

            # Save report
            report_path_obj = Path(report_path)
            try:
                if report_path_obj.suffix.lower() == ".csv":
                    invalid_df.to_csv(report_path_obj, index=True)
                elif report_path_obj.suffix.lower() in [".xlsx", ".xls"]:
                    invalid_df.to_excel(report_path_obj, index=True)
                else:
                    invalid_df.to_csv(report_path_obj, index=True)
            except (IOError, PermissionError) as e:
                raise ETLForgeError(
                    f"Failed to save validation report to {report_path}: {e}"
                ) from e

        return result

    def print_validation_summary(self, result: ValidationResult):
        """Print a summary of validation results."""
        print("\n" + "=" * 50)
        print("VALIDATION SUMMARY")
        print("=" * 50)
        print(f"Total rows: {result.summary['total_rows']}")
        print(f"Valid rows: {result.summary['valid_rows']}")
        print(f"Invalid rows: {result.summary['invalid_rows']}")
        print(f"Columns checked: {result.summary['columns_checked']}")

        if result.summary["missing_columns"]:
            print(f"Missing columns: {', '.join(result.summary['missing_columns'])}")

        if result.summary["extra_columns"]:
            print(f"Extra columns: {', '.join(result.summary['extra_columns'])}")

        print(f"\nValidation: {'PASSED' if result.is_valid else 'FAILED'}")

        if not result.is_valid:
            print(f"Total errors: {len(result.errors)}")

            # Group errors by type
            error_types = {}
            for error in result.errors:
                error_type = error["type"]
                if error_type not in error_types:
                    error_types[error_type] = 0
                error_types[error_type] += 1

            print("\nError breakdown:")
            for error_type, count in error_types.items():
                print(f"  {error_type}: {count}")

        print("=" * 50 + "\n")
