"""
Unit tests for the DataValidator class.
"""

import pytest
import pandas as pd
import tempfile
import os
from etltest.validator import DataValidator, ValidationResult


class TestValidationResult:
    """Test cases for ValidationResult."""
    
    def test_init(self):
        """Test ValidationResult initialization."""
        result = ValidationResult()
        assert result.is_valid is True
        assert result.errors == []
        assert result.invalid_rows == []
        assert result.summary['total_rows'] == 0
    
    def test_add_error(self):
        """Test adding validation errors."""
        result = ValidationResult()
        result.add_error('test_error', 'test_column', 1, 'Test message')
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0]['type'] == 'test_error'
        assert result.errors[0]['column'] == 'test_column'
        assert result.errors[0]['row'] == 1
        assert result.errors[0]['message'] == 'Test message'
        assert 1 in result.invalid_rows


class TestDataValidator:
    """Test cases for DataValidator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_schema = {
            'fields': [
                {
                    'name': 'id',
                    'type': 'int',
                    'unique': True,
                    'nullable': False,
                    'range': {'min': 1, 'max': 100}
                },
                {
                    'name': 'name',
                    'type': 'string',
                    'nullable': False,
                    'length': {'min': 3, 'max': 20}
                },
                {
                    'name': 'score',
                    'type': 'float',
                    'nullable': True,
                    'range': {'min': 0.0, 'max': 100.0}
                },
                {
                    'name': 'category',
                    'type': 'category',
                    'nullable': False,
                    'values': ['A', 'B', 'C']
                },
                {
                    'name': 'date_field',
                    'type': 'date',
                    'nullable': False,
                    'format': '%Y-%m-%d'
                }
            ]
        }
        
        # Valid test data
        self.valid_data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'score': [95.5, None, 87.2],
            'category': ['A', 'B', 'C'],
            'date_field': ['2023-01-01', '2023-01-02', '2023-01-03']
        })
        
        # Invalid test data
        self.invalid_data = pd.DataFrame({
            'id': [1, 1, 3],  # Duplicate
            'name': ['Alice', 'B', None],  # Too short and null
            'score': [95.5, 150.0, -10.0],  # Out of range
            'category': ['A', 'D', 'C'],  # Invalid category
            'date_field': ['2023-01-01', 'invalid-date', '2023-01-03']  # Invalid date
        })
    
    def test_init_with_schema_dict(self):
        """Test initialization with schema dictionary."""
        validator = DataValidator(self.test_schema)
        assert validator.schema == self.test_schema
    
    def test_init_empty(self):
        """Test initialization without schema."""
        validator = DataValidator()
        assert validator.schema is None
    
    def test_load_schema_dict(self):
        """Test loading schema from dictionary."""
        validator = DataValidator()
        validator.load_schema(self.test_schema)
        assert validator.schema == self.test_schema
    
    def test_validate_column_existence_valid(self):
        """Test column existence validation with valid data."""
        validator = DataValidator(self.test_schema)
        result = ValidationResult()
        validator._validate_column_existence(self.valid_data, result)
        
        assert result.is_valid is True
        assert len(result.summary['missing_columns']) == 0
        assert len(result.summary['extra_columns']) == 0
    
    def test_validate_column_existence_missing(self):
        """Test column existence validation with missing columns."""
        validator = DataValidator(self.test_schema)
        result = ValidationResult()
        
        # Data missing the 'score' column
        incomplete_data = self.valid_data.drop('score', axis=1)
        validator._validate_column_existence(incomplete_data, result)
        
        assert result.is_valid is False
        assert 'score' in result.summary['missing_columns']
    
    def test_validate_column_existence_extra(self):
        """Test column existence validation with extra columns."""
        validator = DataValidator(self.test_schema)
        result = ValidationResult()
        
        # Data with extra column
        extra_data = self.valid_data.copy()
        extra_data['extra_col'] = [1, 2, 3]
        validator._validate_column_existence(extra_data, result)
        
        assert result.is_valid is True  # Extra columns don't make it invalid
        assert 'extra_col' in result.summary['extra_columns']
    
    def test_validate_data_types_valid(self):
        """Test data type validation with valid data."""
        validator = DataValidator(self.test_schema)
        result = ValidationResult()
        validator._validate_data_types(self.valid_data, result)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_data_types_invalid(self):
        """Test data type validation with invalid data."""
        validator = DataValidator(self.test_schema)
        result = ValidationResult()
        
        # Create data with type errors
        bad_data = pd.DataFrame({
            'id': ['not_int', 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'score': ['not_float', None, 87.2],
            'category': ['A', 'B', 'C'],
            'date_field': ['2023-01-01', '2023-01-02', '2023-01-03']
        })
        
        validator._validate_data_types(bad_data, result)
        
        assert result.is_valid is False
        assert len(result.errors) >= 2  # At least id and score type errors
    
    def test_validate_constraints_null_values(self):
        """Test null value constraint validation."""
        validator = DataValidator(self.test_schema)
        result = ValidationResult()
        
        # Data with null in non-nullable column
        bad_data = self.valid_data.copy()
        bad_data.loc[0, 'name'] = None
        
        validator._validate_constraints(bad_data, result)
        
        assert result.is_valid is False
        null_errors = [e for e in result.errors if e['type'] == 'null_value']
        assert len(null_errors) >= 1
    
    def test_validate_constraints_unique_values(self):
        """Test unique constraint validation."""
        validator = DataValidator(self.test_schema)
        result = ValidationResult()
        
        # Data with duplicate in unique column
        bad_data = self.valid_data.copy()
        bad_data.loc[1, 'id'] = 1  # Duplicate id
        
        validator._validate_constraints(bad_data, result)
        
        assert result.is_valid is False
        duplicate_errors = [e for e in result.errors if e['type'] == 'duplicate_value']
        assert len(duplicate_errors) >= 1
    
    def test_validate_constraints_range_values(self):
        """Test range constraint validation."""
        validator = DataValidator(self.test_schema)
        result = ValidationResult()
        
        # Data with out-of-range values
        bad_data = self.valid_data.copy()
        bad_data.loc[0, 'score'] = 150.0  # Above max
        bad_data.loc[1, 'id'] = 0  # Below min
        
        validator._validate_constraints(bad_data, result)
        
        assert result.is_valid is False
        range_errors = [e for e in result.errors if e['type'] == 'range_violation']
        assert len(range_errors) >= 2
    
    def test_validate_constraints_category_values(self):
        """Test category constraint validation."""
        validator = DataValidator(self.test_schema)
        result = ValidationResult()
        
        # Data with invalid category
        bad_data = self.valid_data.copy()
        bad_data.loc[0, 'category'] = 'Invalid'
        
        validator._validate_constraints(bad_data, result)
        
        assert result.is_valid is False
        category_errors = [e for e in result.errors if e['type'] == 'invalid_category']
        assert len(category_errors) >= 1
    
    def test_is_valid_date(self):
        """Test date validation helper method."""
        validator = DataValidator(self.test_schema)
        
        assert validator._is_valid_date('2023-01-01', '%Y-%m-%d') is True
        assert validator._is_valid_date('2023/01/01', '%Y-%m-%d') is False
        assert validator._is_valid_date('invalid', '%Y-%m-%d') is False
        assert validator._is_valid_date(123, '%Y-%m-%d') is False
    
    def test_validate_valid_data(self):
        """Test full validation with valid data."""
        validator = DataValidator(self.test_schema)
        result = validator.validate(self.valid_data)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.invalid_rows) == 0
        assert result.summary['valid_rows'] == 3
        assert result.summary['invalid_rows'] == 0
    
    def test_validate_invalid_data(self):
        """Test full validation with invalid data."""
        validator = DataValidator(self.test_schema)
        result = validator.validate(self.invalid_data)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert len(result.invalid_rows) > 0
        assert result.summary['invalid_rows'] > 0
    
    def test_validate_no_schema(self):
        """Test validation without loaded schema."""
        validator = DataValidator()
        with pytest.raises(ValueError, match="No schema loaded"):
            validator.validate(self.valid_data)
    
    def test_validate_and_report(self):
        """Test validation with report generation."""
        validator = DataValidator(self.test_schema)
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            result = validator.validate_and_report(self.invalid_data, temp_path)
            
            assert result.is_valid is False
            assert os.path.exists(temp_path)
            
            # Check report content
            report_df = pd.read_csv(temp_path)
            assert len(report_df) > 0
            assert 'validation_errors' in report_df.columns
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_load_data_csv(self):
        """Test loading CSV data."""
        validator = DataValidator(self.test_schema)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.valid_data.to_csv(f.name, index=False)
            temp_path = f.name
        
        try:
            df = validator.load_data(temp_path)
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 3
            assert len(df.columns) == 5
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_unsupported_file_format(self):
        """Test handling of unsupported file formats."""
        validator = DataValidator(self.test_schema)
        
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported data file format"):
                validator.load_data(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


def test_validation_summary_output(capsys):
    """Test validation summary printing."""
    schema = {
        'fields': [
            {'name': 'test_col', 'type': 'int', 'nullable': False}
        ]
    }
    validator = DataValidator(schema)
    
    # Create simple invalid data
    invalid_data = pd.DataFrame({'test_col': [1, None, 3]})
    result = validator.validate(invalid_data)
    
    validator.print_validation_summary(result)
    captured = capsys.readouterr()
    
    assert "VALIDATION SUMMARY" in captured.out
    assert "FAILED" in captured.out
    assert "Total rows: 3" in captured.out 