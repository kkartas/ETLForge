# ETLForge

A Python library for generating synthetic test data and validating ETL outputs. ETLForge provides both command-line tools and library functions to help you create realistic test datasets and validate data quality.

## Features

### 🎲 Test Data Generator
- Generate synthetic data based on YAML/JSON schema definitions
- Support for multiple data types: `int`, `float`, `string`, `date`, `category`
- Advanced constraints: ranges, uniqueness, nullable fields, categorical values
- Integration with Faker for realistic string generation
- Export to CSV or Excel formats

### ✅ Data Validator
- Validate CSV/Excel files against schema definitions
- Comprehensive validation checks:
  - Column existence
  - Data type matching
  - Value constraints (ranges, categories)
  - Uniqueness validation
  - Null value validation
  - Date format validation
- Generate detailed reports of invalid rows

### 🔧 Dual Interface
- **Command-line interface** for quick operations
- **Python library** for integration into existing workflows

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

You can also install it directly from GitHub:
```bash
pip install git+https://github.com/kkartas/etl-forge.git
```

### Optional Dependencies

For enhanced string generation with realistic data:
```bash
pip install faker
```

## Quick Start

### 1. Create a Schema

Create a `schema.yaml` file defining your data structure:

```yaml
fields:
  - name: id
    type: int
    unique: true
    nullable: false
    range:
      min: 1
      max: 10000

  - name: name
    type: string
    nullable: false
    faker_template: name

  - name: department
    type: category
    nullable: false
    values:
      - Engineering
      - Marketing
      - Sales
```

### 2. Generate Test Data

**Command Line:**
```bash
etl-forge generate --schema schema.yaml --rows 500 --output sample.csv
```

**Python Library:**
```python
from etl_forge import DataGenerator

generator = DataGenerator('schema.yaml')
df = generator.generate_data(500)
generator.save_data(df, 'sample.csv')
```

### 3. Validate Data

**Command Line:**
```bash
etl-forge check --input sample.csv --schema schema.yaml --report invalid_rows.csv
```

**Python Library:**
```python
from etl_forge import DataValidator

validator = DataValidator('schema.yaml')
result = validator.validate('sample.csv')
print(f"Validation passed: {result.is_valid}")
```

## Schema Definition

### Supported Field Types

#### Integer (`int`)
```yaml
- name: age
  type: int
  nullable: false
  range:
    min: 18
    max: 65
  unique: false
```

#### Float (`float`)
```yaml
- name: salary
  type: float
  nullable: true
  range:
    min: 30000.0
    max: 150000.0
  precision: 2
  null_rate: 0.1
```

#### String (`string`)
```yaml
- name: email
  type: string
  nullable: false
  unique: true
  length:
    min: 10
    max: 50
  faker_template: email  # Optional: uses Faker library
```

#### Date (`date`)
```yaml
- name: hire_date
  type: date
  nullable: false
  range:
    start: '2020-01-01'
    end: '2024-12-31'
  format: '%Y-%m-%d'
```

#### Category (`category`)
```yaml
- name: status
  type: category
  nullable: false
  values:
    - Active
    - Inactive
    - Pending
```

### Schema Constraints

- **`nullable`**: Allow null values (default: `false`)
- **`unique`**: Ensure all values are unique (default: `false`)
- **`range`**: Define min/max values for numeric types or start/end dates
- **`values`**: List of allowed values for categorical fields
- **`length`**: Min/max length for string fields
- **`precision`**: Decimal places for float fields
- **`format`**: Date format string (default: `'%Y-%m-%d'`)
- **`faker_template`**: Faker method name for realistic string generation
- **`null_rate`**: Probability of null values when `nullable: true` (default: 0.1)

## Command Line Interface

### Generate Data
```bash
etl-forge generate [OPTIONS]

Options:
  -s, --schema PATH     Path to schema file (YAML or JSON) [required]
  -r, --rows INTEGER    Number of rows to generate (default: 100)
  -o, --output PATH     Output file path (CSV or Excel) [required]
  -f, --format [csv|excel]  Output format (auto-detected if not specified)
```

### Validate Data
```bash
etl-forge check [OPTIONS]

Options:
  -i, --input PATH      Path to input data file [required]
  -s, --schema PATH     Path to schema file [required]
  -r, --report PATH     Path to save invalid rows report (optional)
  -v, --verbose         Show detailed validation errors
```

### Create Example Schema
```bash
etl-forge create-example-schema example_schema.yaml
```

## Library Usage

### Data Generation

```python
from etl_forge import DataGenerator

# Initialize with schema
generator = DataGenerator('schema.yaml')

# Generate data
df = generator.generate_data(1000)

# Save to file
generator.save_data(df, 'output.csv')

# Or do both in one step
df = generator.generate_and_save(1000, 'output.xlsx', 'excel')
```

### Data Validation

```python
from etl_forge import DataValidator

# Initialize validator
validator = DataValidator('schema.yaml')

# Validate data
result = validator.validate('data.csv')

# Check results
if result.is_valid:
    print("✅ Data is valid!")
else:
    print(f"❌ Found {len(result.errors)} validation errors")
    print(f"Invalid rows: {len(result.invalid_rows)}")

# Generate report
result = validator.validate_and_report('data.csv', 'errors.csv')

# Print summary
validator.print_validation_summary(result)
```

### Advanced Usage

```python
# Use schema as dictionary
schema_dict = {
    'fields': [
        {'name': 'id', 'type': 'int', 'unique': True},
        {'name': 'name', 'type': 'string', 'faker_template': 'name'}
    ]
}

generator = DataGenerator(schema_dict)
validator = DataValidator(schema_dict)

# Validate DataFrame directly
import pandas as pd
df = pd.read_csv('data.csv')
result = validator.validate(df)
```

## Faker Integration

When the `faker` library is installed, you can use realistic data generation:

```yaml
- name: first_name
  type: string
  faker_template: first_name

- name: address
  type: string
  faker_template: address

- name: phone
  type: string
  faker_template: phone_number
```

Common Faker templates:
- `name`, `first_name`, `last_name`
- `email`, `phone_number`
- `address`, `city`, `country`
- `company`, `job`
- `date`, `time`
- And many more! See [Faker documentation](https://faker.readthedocs.io/)

## Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest tests/ --cov=etl_forge --cov-report=html
```

## Contributing

Contributions are welcome! Please see the [Contributing Guidelines](CONTRIBUTING.md) for more details.

We adhere to a [Code of Conduct](CODE_OF_CONDUCT.md) for all participants.

## Authors and Citation

This project is developed and maintained by Kyriakos Kartas.

If you use ETLForge in your research, please cite it using the following metadata from [CITATION.cff](CITATION.cff).

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a history of changes.

## Documentation

Full HTML documentation, including a user guide and a complete API reference, can be built locally:

```bash
cd docs
make html
```

Then open `docs/build/html/index.html` in your browser.

## Running Tests

To run the full test suite and view a coverage report:

```bash
pip install -e ".[dev]"
pytest --cov=etl_forge
```

## Contributing

Contributions are welcome! Please read `CONTRIBUTING.md` for details on how to set up your development environment, run tests, and submit a pull request.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Citation

If you use `ETLForge` in your research or work, please cite it using the information in `CITATION.cff`.

To run the performance benchmarks, use the following command:
```bash
pytest --cov=etl_forge
```

Then, to visualize the results: 