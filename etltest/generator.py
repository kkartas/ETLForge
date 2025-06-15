"""
Data generator module for creating synthetic test data based on schema definitions.
"""

import pandas as pd
import numpy as np
import yaml
import json
from datetime import datetime, timedelta
import random
import string
from typing import Dict, Any, List, Union
from pathlib import Path
from . import ETLTestError

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
            ETLTestError: If the schema file cannot be found or parsed.
        """
        self.faker = Faker() if FAKER_AVAILABLE else None
        self.schema: Dict[str, Any] = {}
        
        if schema_path:
            self.load_schema(schema_path)
    
    def load_schema(self, schema_path: Union[str, Path, dict]):
        """
        Loads a schema from a file path or a dictionary.

        Args:
            schema_path: The path to a YAML/JSON schema file or a dictionary
                containing the schema definition.

        Raises:
            ETLTestError: If the schema file is not found, has an unsupported
                format, or cannot be parsed.
        """
        if isinstance(schema_path, dict):
            self.schema = schema_path
            return

        schema_path_obj = Path(schema_path)
        if not schema_path_obj.exists():
            raise ETLTestError(f"Schema file not found at: {schema_path}")

        suffix = schema_path_obj.suffix.lower()
        try:
            with open(schema_path_obj, 'r', encoding='utf-8') as file:
                if suffix in ['.yaml', '.yml']:
                    self.schema = yaml.safe_load(file)
                elif suffix == '.json':
                    self.schema = json.load(file)
                else:
                    raise ETLTestError(f"Unsupported schema file format: {suffix}")
        except (IOError, yaml.YAMLError, json.JSONDecodeError) as e:
            raise ETLTestError(f"Failed to load or parse schema file: {e}") from e
    
    def _generate_int_column(self, field_config: Dict[str, Any], num_rows: int) -> List[Union[int, None]]:
        """Generate integer column data."""
        min_val = field_config.get('range', {}).get('min', 0)
        max_val = field_config.get('range', {}).get('max', 100)
        nullable = field_config.get('nullable', False)
        unique = field_config.get('unique', False)
        null_rate = field_config.get('null_rate', 0.1) if nullable else 0
        
        if unique:
            if max_val - min_val + 1 < num_rows:
                raise ETLTestError(f"Cannot generate {num_rows} unique integers for column '{field_config['name']}' in range [{min_val}, {max_val}]")
            # This is inefficient for large ranges, but sufficient for this implementation.
            # A more robust solution might use random sampling without replacement.
            pool = list(range(min_val, max_val + 1))
            values = random.sample(pool, num_rows)
        else:
            values = [random.randint(min_val, max_val) for _ in range(num_rows)]
        
        # Add nulls if nullable
        if nullable and null_rate > 0:
            null_count = int(num_rows * null_rate)
            null_indices = random.sample(range(num_rows), null_count)
            for idx in null_indices:
                values[idx] = None
        
        return values
    
    def _generate_float_column(self, field_config: Dict[str, Any], num_rows: int) -> List[Union[float, None]]:
        """Generate float column data."""
        min_val = field_config.get('range', {}).get('min', 0.0)
        max_val = field_config.get('range', {}).get('max', 100.0)
        precision = field_config.get('precision', 2)
        nullable = field_config.get('nullable', False)
        null_rate = field_config.get('null_rate', 0.1) if nullable else 0
        
        values = [round(random.uniform(min_val, max_val), precision) for _ in range(num_rows)]
        
        # Add nulls if nullable
        if nullable and null_rate > 0:
            null_count = int(num_rows * null_rate)
            null_indices = random.sample(range(num_rows), null_count)
            for idx in null_indices:
                values[idx] = None
        
        return values
    
    def _generate_string_column(self, field_config: Dict[str, Any], num_rows: int) -> List[Union[str, None]]:
        """Generate string column data."""
        min_length = field_config.get('length', {}).get('min', 5)
        max_length = field_config.get('length', {}).get('max', 20)
        nullable = field_config.get('nullable', False)
        unique = field_config.get('unique', False)
        null_rate = field_config.get('null_rate', 0.1) if nullable else 0
        faker_template = field_config.get('faker_template')
        
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
                    value = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
                    values.append(value)
        else:
            # Generate random strings
            if unique:
                values_set = set()
                while len(values_set) < num_rows:
                    length = random.randint(min_length, max_length)
                    value = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
                    values_set.add(value)
                values = list(values_set)
                random.shuffle(values)
            else:
                for _ in range(num_rows):
                    length = random.randint(min_length, max_length)
                    value = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
                    values.append(value)
        
        # Add nulls if nullable
        if nullable and null_rate > 0:
            null_count = int(num_rows * null_rate)
            null_indices = random.sample(range(num_rows), null_count)
            for idx in null_indices:
                values[idx] = None
        
        return values
    
    def _generate_date_column(self, field_config: Dict[str, Any], num_rows: int) -> List[Union[str, None]]:
        """Generate date column data."""
        start_date = field_config.get('range', {}).get('start', '2020-01-01')
        end_date = field_config.get('range', {}).get('end', '2024-12-31')
        date_format = field_config.get('format', '%Y-%m-%d')
        nullable = field_config.get('nullable', False)
        null_rate = field_config.get('null_rate', 0.1) if nullable else 0
        
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
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
    
    def _generate_category_column(self, field_config: Dict[str, Any], num_rows: int) -> List[Union[str, None]]:
        """Generate categorical column data."""
        values_list = field_config.get('values', ['A', 'B', 'C'])
        nullable = field_config.get('nullable', False)
        null_rate = field_config.get('null_rate', 0.1) if nullable else 0
        
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
            ETLTestError: If no schema has been loaded or if an unsupported
                field type is encountered in the schema.
        """
        if not self.schema:
            raise ETLTestError("No schema loaded. Use load_schema() first.")
        
        data = {}
        
        for field in self.schema.get('fields', []):
            field_name = field['name']
            field_type = field['type'].lower()
            
            try:
                if field_type == 'int':
                    data[field_name] = self._generate_int_column(field, num_rows)
                elif field_type == 'float':
                    data[field_name] = self._generate_float_column(field, num_rows)
                elif field_type == 'string':
                    data[field_name] = self._generate_string_column(field, num_rows)
                elif field_type == 'date':
                    data[field_name] = self._generate_date_column(field, num_rows)
                elif field_type == 'category':
                    data[field_name] = self._generate_category_column(field, num_rows)
                else:
                    raise ETLTestError(f"Unsupported field type: '{field_type}' for column '{field_name}'")
            except ETLTestError:
                raise  # Re-raise our own exceptions
            except Exception as e:
                raise ETLTestError(f"Failed to generate data for column '{field_name}': {e}") from e
        
        return pd.DataFrame(data)
    
    def save_data(self, df: pd.DataFrame, output_path: Union[str, Path], file_format: str = None):
        """
        Saves the generated DataFrame to a file (CSV or Excel).

        Args:
            df: The pandas DataFrame to save.
            output_path: The destination file path.
            file_format: The output format ('csv' or 'excel'). If not provided,
                it is inferred from the file extension of `output_path`.

        Raises:
            ETLTestError: If the file format is unsupported or if an error
                occurs during file writing.
        """
        output_path_obj = Path(output_path)
        
        if file_format is None:
            file_format = 'excel' if output_path_obj.suffix.lower() in ['.xlsx', '.xls'] else 'csv'
        
        try:
            if file_format.lower() == 'csv':
                df.to_csv(output_path_obj, index=False)
            elif file_format.lower() == 'excel':
                df.to_excel(output_path_obj, index=False)
            else:
                raise ETLTestError(f"Unsupported file format: {file_format}")
        except (IOError, PermissionError) as e:
            raise ETLTestError(f"Failed to save data to {output_path}: {e}") from e
    
    def generate_and_save(self, num_rows: int, output_path: Union[str, Path], file_format: str = None):
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