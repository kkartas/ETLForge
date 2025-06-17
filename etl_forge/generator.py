"""
Data generator module for creating synthetic test data based on schema definitions.
"""

import pandas as pd
import yaml
import json
from datetime import datetime, timedelta
import random
import string
from typing import Dict, Any, List, Union
from pathlib import Path
from .exceptions import ETLForgeError

try:
    from faker import Faker

    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False


class DataGenerator:
    """
    Generates synthetic test data based on a declarative schema.

    This class reads a YAML or JSON schema, generates data according to the
    specified types and constraints, and can save the output to CSV or Excel.
    """

    def __init__(self, schema_path: Union[str, Path, dict] = None):
        """
        Initializes the DataGenerator.

        Args:
            schema_path: The path to a YAML/JSON schema file or a dictionary
                containing the schema definition.

        Raises:
            ETLForgeError: If the schema cannot be loaded or is invalid.
        """
        self.faker = Faker() if FAKER_AVAILABLE else None
        self.schema: Dict[str, Any] = {}

        if schema_path:
            self.load_schema(schema_path)

    def load_schema(self, schema_path: Union[str, Path, dict]):
        """
        Loads and validates a schema from a file path or a dictionary.

        This method supports both file paths (YAML or JSON) and direct
        dictionary objects as input. It orchestrates the loading and
        subsequent validation of the schema.

        Args:
            schema_path: The path to a YAML/JSON schema file or a dictionary
                containing the schema definition.

        Raises:
            ETLForgeError: If `schema_path` points to a file that is not
                found, has an unsupported extension, or if the file cannot
                be parsed due to syntax errors or I/O issues. Also raised
                if the loaded schema fails any validation checks.
        """
        if isinstance(schema_path, dict):
            self.schema = schema_path
            self._validate_schema()
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
            raise ETLForgeError(f"Failed to load or parse a schema file: {e}") from e
        
        self._validate_schema()

    def _validate_schema(self):
        """
        Validates the loaded schema for correctness and completeness.
        
        This internal method checks for the presence of required keys ('fields'),
        ensures that field definitions are correct, and validates constraints
        to prevent errors during data generation.

        Raises:
            ETLForgeError: If the schema is empty, missing the 'fields' key,
                contains duplicate field names, uses unsupported data types,
                or has invalid configurations for `range`, `length`, `values`,
                or `null_rate`.
        """
        if not self.schema:
            raise ETLForgeError("Schema is empty or None")
        
        if "fields" not in self.schema:
            raise ETLForgeError("Schema must contain a 'fields' key")
        
        fields = self.schema["fields"]
        if not isinstance(fields, list) or len(fields) == 0:
            raise ETLForgeError("Schema 'fields' must be a non-empty list")
        
        field_names = set()
        supported_types = {"int", "float", "string", "date", "category"}
        
        for i, field in enumerate(fields):
            if not isinstance(field, dict):
                raise ETLForgeError(f"Field at index {i} must be a dictionary")
            
            # Check required fields
            if "name" not in field:
                raise ETLForgeError(f"Field at index {i} is missing required 'name' property")
            
            if "type" not in field:
                raise ETLForgeError(f"Field '{field.get('name', i)}' is missing required 'type' property")
            
            field_name = field["name"]
            field_type = field["type"]
            
            # Check for duplicate field names
            if field_name in field_names:
                raise ETLForgeError(f"Duplicate field name '{field_name}' found")
            field_names.add(field_name)
            
            # Validate field type
            if field_type not in supported_types:
                raise ETLForgeError(
                    f"Field '{field_name}' has unsupported type '{field_type}'. "
                    f"Supported types: {', '.join(sorted(supported_types))}"
                )
            
            # Type-specific validations
            if field_type in ["int", "float"] and "range" in field:
                range_config = field["range"]
                if not isinstance(range_config, dict):
                    raise ETLForgeError(f"Field '{field_name}' range must be a dictionary")
                
                if "min" in range_config and "max" in range_config:
                    if range_config["min"] >= range_config["max"]:
                        raise ETLForgeError(f"Field '{field_name}' min value must be less than max value")
            
            if field_type == "category" and "values" in field:
                values = field["values"]
                if not isinstance(values, list) or len(values) == 0:
                    raise ETLForgeError(f"Field '{field_name}' values must be a non-empty list")
            
            if field_type == "string" and "length" in field:
                length_config = field["length"]
                if not isinstance(length_config, dict):
                    raise ETLForgeError(f"Field '{field_name}' length must be a dictionary")
                
                if "min" in length_config and "max" in length_config:
                    if length_config["min"] >= length_config["max"]:
                        raise ETLForgeError(f"Field '{field_name}' min length must be less than max length")
            
            # Validate null_rate
            if "null_rate" in field:
                null_rate = field["null_rate"]
                if not isinstance(null_rate, (int, float)) or not (0 <= null_rate <= 1):
                    raise ETLForgeError(f"Field '{field_name}' null_rate must be a number between 0 and 1")

    def _generate_int_column(
        self, field_config: Dict[str, Any], num_rows: int
    ) -> List[Union[int, None]]:
        """Generate integer column data."""
        min_val = field_config.get("range", {}).get("min", 0)
        max_val = field_config.get("range", {}).get("max", 100)
        nullable = field_config.get("nullable", False)
        unique = field_config.get("unique", False)
        null_rate = field_config.get("null_rate", 0.1) if nullable else 0

        if unique:
            if max_val - min_val + 1 < num_rows:
                raise ETLForgeError(
                    f"Cannot generate {num_rows} unique integers for column '{field_config['name']}' in range [{min_val}, {max_val}]"
                )
            
            # Optimized unique integer generation for large ranges
            range_size = max_val - min_val + 1
            if range_size < num_rows * 10:
                # For small ranges, use the original approach
                pool = list(range(min_val, max_val + 1))
                values = random.sample(pool, num_rows)
            else:
                # For large ranges, use set-based sampling to avoid memory issues
                values = set()
                max_attempts = num_rows * 10  # Prevent infinite loops
                attempts = 0
                while len(values) < num_rows and attempts < max_attempts:
                    values.add(random.randint(min_val, max_val))
                    attempts += 1
                
                if len(values) < num_rows:
                    raise ETLForgeError(
                        f"Could not generate {num_rows} unique integers for column '{field_config['name']}' "
                        f"after {max_attempts} attempts. Consider expanding the range."
                    )
                values = list(values)
                random.shuffle(values)
        else:
            values = [random.randint(min_val, max_val) for _ in range(num_rows)]

        # Add nulls if nullable
        if nullable and null_rate > 0:
            null_count = int(num_rows * null_rate)
            null_indices = random.sample(range(num_rows), null_count)
            for idx in null_indices:
                values[idx] = None

        return values

    def _generate_float_column(
        self, field_config: Dict[str, Any], num_rows: int
    ) -> List[Union[float, None]]:
        """Generate float column data."""
        min_val = field_config.get("range", {}).get("min", 0.0)
        max_val = field_config.get("range", {}).get("max", 100.0)
        precision = field_config.get("precision", 2)
        nullable = field_config.get("nullable", False)
        null_rate = field_config.get("null_rate", 0.1) if nullable else 0

        values = [
            round(random.uniform(min_val, max_val), precision) for _ in range(num_rows)
        ]

        # Add nulls if nullable
        if nullable and null_rate > 0:
            null_count = int(num_rows * null_rate)
            null_indices = random.sample(range(num_rows), null_count)
            for idx in null_indices:
                values[idx] = None

        return values

    def _generate_string_column(
        self, field_config: Dict[str, Any], num_rows: int
    ) -> List[Union[str, None]]:
        """Generate string column data."""
        min_length = field_config.get("length", {}).get("min", 5)
        max_length = field_config.get("length", {}).get("max", 20)
        nullable = field_config.get("nullable", False)
        unique = field_config.get("unique", False)
        null_rate = field_config.get("null_rate", 0.1) if nullable else 0
        faker_template = field_config.get("faker_template")

        values = []

        if faker_template and self.faker:
            # Use Faker template
            for _ in range(num_rows):
                try:
                    value = getattr(self.faker, faker_template)()
                    values.append(str(value))
                except AttributeError:
                    # Fallback to random string if faker method doesn't exist
                    length = random.randint(min_length, max_length)
                    value = "".join(
                        random.choices(string.ascii_letters + string.digits, k=length)
                    )
                    values.append(value)
        else:
            # Generate random strings
            if unique:
                values_set = set()
                max_attempts = num_rows * 100  # Prevent infinite loops for unique strings
                attempts = 0
                while len(values_set) < num_rows and attempts < max_attempts:
                    length = random.randint(min_length, max_length)
                    value = "".join(
                        random.choices(string.ascii_letters + string.digits, k=length)
                    )
                    values_set.add(value)
                    attempts += 1
                
                if len(values_set) < num_rows:
                    raise ETLForgeError(
                        f"Could not generate {num_rows} unique strings for column '{field_config['name']}' "
                        f"after {max_attempts} attempts. Consider increasing string length range."
                    )
                values = list(values_set)
                random.shuffle(values)
            else:
                for _ in range(num_rows):
                    length = random.randint(min_length, max_length)
                    value = "".join(
                        random.choices(string.ascii_letters + string.digits, k=length)
                    )
                    values.append(value)

        # Add nulls if nullable
        if nullable and null_rate > 0:
            null_count = int(num_rows * null_rate)
            null_indices = random.sample(range(num_rows), null_count)
            for idx in null_indices:
                values[idx] = None

        return values

    def _generate_date_column(
        self, field_config: Dict[str, Any], num_rows: int
    ) -> List[Union[str, None]]:
        """Generate date column data."""
        start_date = field_config.get("range", {}).get("start", "2020-01-01")
        end_date = field_config.get("range", {}).get("end", "2024-12-31")
        date_format = field_config.get("format", "%Y-%m-%d")
        nullable = field_config.get("nullable", False)
        null_rate = field_config.get("null_rate", 0.1) if nullable else 0

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        values = []
        for _ in range(num_rows):
            random_days = random.randint(0, (end_dt - start_dt).days)
            random_date = start_dt + timedelta(days=random_days)
            values.append(random_date.strftime(date_format))

        # Add nulls if nullable
        if nullable and null_rate > 0:
            null_count = int(num_rows * null_rate)
            null_indices = random.sample(range(num_rows), null_count)
            for idx in null_indices:
                values[idx] = None

        return values

    def _generate_category_column(
        self, field_config: Dict[str, Any], num_rows: int
    ) -> List[Union[str, None]]:
        """Generate categorical column data."""
        values_list = field_config.get("values", ["A", "B", "C"])
        nullable = field_config.get("nullable", False)
        null_rate = field_config.get("null_rate", 0.1) if nullable else 0

        values = [random.choice(values_list) for _ in range(num_rows)]

        # Add nulls if nullable
        if nullable and null_rate > 0:
            null_count = int(num_rows * null_rate)
            null_indices = random.sample(range(num_rows), null_count)
            for idx in null_indices:
                values[idx] = None

        return values

    def generate_data(self, num_rows: int) -> pd.DataFrame:
        """
        Generates a pandas DataFrame with synthetic data.

        This is the main method for data generation. It iterates through the
        fields defined in the schema and generates data for each column.

        Args:
            num_rows: The number of rows of data to generate.

        Returns:
            A pandas DataFrame containing the synthetic data.

        Raises:
            ETLForgeError: If no schema has been loaded, if an unsupported
                field type is encountered, or if data generation fails for a
                specific column (e.g., unable to generate enough unique values
                for the given constraints).
        """
        if not self.schema:
            raise ETLForgeError("No schema loaded. Use load_schema() first.")

        data = {}

        for field in self.schema.get("fields", []):
            field_name = field["name"]
            field_type = field["type"].lower()

            try:
                if field_type == "int":
                    data[field_name] = self._generate_int_column(field, num_rows)
                elif field_type == "float":
                    data[field_name] = self._generate_float_column(field, num_rows)
                elif field_type == "string":
                    data[field_name] = self._generate_string_column(field, num_rows)
                elif field_type == "date":
                    data[field_name] = self._generate_date_column(field, num_rows)
                elif field_type == "category":
                    data[field_name] = self._generate_category_column(field, num_rows)
                else:
                    raise ETLForgeError(
                        f"Unsupported field type: '{field_type}' for column '{field_name}'"
                    )
            except ETLForgeError:
                raise
            except Exception as e:
                raise ETLForgeError(
                    f"Failed to generate data for column '{field_name}': {e}"
                ) from e

        return pd.DataFrame(data)

    def save_data(
        self, df: pd.DataFrame, output_path: Union[str, Path], file_format: str = None
    ):
        """
        Saves the generated DataFrame to a file (CSV or Excel).

        Args:
            df: The pandas DataFrame to save.
            output_path: The destination file path.
            file_format: The output format ('csv' or 'excel'). If not provided,
                it is inferred from the file extension of `output_path`.

        Raises:
            ETLForgeError: If the file format is unsupported or if an error
                occurs during file writing.
        """
        output_path_obj = Path(output_path)

        if file_format is None:
            suffix = output_path_obj.suffix.lower()
            if suffix == ".csv":
                file_format = "csv"
            elif suffix in [".xls", ".xlsx"]:
                file_format = "excel"
            else:
                raise ETLForgeError(
                    f"Unsupported file format: could not infer from extension '{suffix}'"
                )

        try:
            if file_format == "csv":
                df.to_csv(output_path_obj, index=False)
            elif file_format == "excel":
                df.to_excel(output_path_obj, index=False)
            else:
                raise ETLForgeError(f"Unsupported file format: {file_format}")
        except IOError as e:
            raise ETLForgeError(f"Failed to save data to {output_path}: {e}") from e

    def generate_and_save(
        self, num_rows: int, output_path: Union[str, Path], file_format: str = None
    ) -> pd.DataFrame:
        """
        Generates data and saves it to a file in a single step.

        Args:
            num_rows: The number of rows of data to generate.
            output_path: The destination file path.
            file_format: The output format ('csv' or 'excel'). If not provided,
                it is inferred from the file extension.

        Returns:
            The generated pandas DataFrame.
        """
        df = self.generate_data(num_rows)
        self.save_data(df, output_path, file_format)
        return df
