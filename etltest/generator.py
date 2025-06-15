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

try:
    from faker import Faker
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False


class DataGenerator:
    """Generate synthetic test data based on schema definitions."""
    
    def __init__(self, schema_path: Union[str, Path, dict] = None):
        """
        Initialize the DataGenerator.
        
        Args:
            schema_path: Path to schema file (YAML/JSON) or dict with schema definition
        """
        self.faker = Faker() if FAKER_AVAILABLE else None
        self.schema = None
        
        if schema_path:
            self.load_schema(schema_path)
    
    def load_schema(self, schema_path: Union[str, Path, dict]):
        """
        Load schema from file or dict.
        
        Args:
            schema_path: Path to schema file or dict with schema
        """
        if isinstance(schema_path, dict):
            self.schema = schema_path
        else:
            schema_path = Path(schema_path)
            
            if schema_path.suffix.lower() in ['.yaml', '.yml']:
                with open(schema_path, 'r', encoding='utf-8') as file:
                    self.schema = yaml.safe_load(file)
            elif schema_path.suffix.lower() == '.json':
                with open(schema_path, 'r', encoding='utf-8') as file:
                    self.schema = json.load(file)
            else:
                raise ValueError(f"Unsupported schema file format: {schema_path.suffix}")
    
    def _generate_int_column(self, field_config: Dict[str, Any], num_rows: int) -> List[Union[int, None]]:
        """Generate integer column data."""
        min_val = field_config.get('range', {}).get('min', 0)
        max_val = field_config.get('range', {}).get('max', 100)
        nullable = field_config.get('nullable', False)
        unique = field_config.get('unique', False)
        null_rate = field_config.get('null_rate', 0.1) if nullable else 0
        
        if unique:
            if max_val - min_val + 1 < num_rows:
                raise ValueError(f"Cannot generate {num_rows} unique integers in range [{min_val}, {max_val}]")
            values = list(range(min_val, min_val + num_rows))
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
        Generate synthetic data based on the loaded schema.
        
        Args:
            num_rows: Number of rows to generate
            
        Returns:
            pd.DataFrame: Generated data
        """
        if not self.schema:
            raise ValueError("No schema loaded. Use load_schema() first.")
        
        data = {}
        
        for field in self.schema.get('fields', []):
            field_name = field['name']
            field_type = field['type'].lower()
            
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
                raise ValueError(f"Unsupported field type: {field_type}")
        
        return pd.DataFrame(data)
    
    def save_data(self, df: pd.DataFrame, output_path: Union[str, Path], file_format: str = None):
        """
        Save generated data to file.
        
        Args:
            df: DataFrame to save
            output_path: Output file path
            file_format: File format ('csv' or 'excel'). If None, inferred from file extension.
        """
        output_path = Path(output_path)
        
        if file_format is None:
            file_format = 'excel' if output_path.suffix.lower() in ['.xlsx', '.xls'] else 'csv'
        
        if file_format.lower() == 'csv':
            df.to_csv(output_path, index=False)
        elif file_format.lower() == 'excel':
            df.to_excel(output_path, index=False)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
    
    def generate_and_save(self, num_rows: int, output_path: Union[str, Path], file_format: str = None) -> pd.DataFrame:
        """
        Generate data and save to file in one step.
        
        Args:
            num_rows: Number of rows to generate
            output_path: Output file path  
            file_format: File format ('csv' or 'excel')
            
        Returns:
            pd.DataFrame: Generated data
        """
        df = self.generate_data(num_rows)
        self.save_data(df, output_path, file_format)
        return df 