# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- JOSS submission preparation including `paper.md`, `CITATION.cff`, and `LICENSE`.
- `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` for community guidelines.
- This `CHANGELOG.md` file.

## [0.1.0] - 2024-12-13

### Added
- Initial release of `ETLTest`.
- **Data Generator**:
  - Generate synthetic data from YAML/JSON schema.
  - Supported types: `int`, `float`, `string`, `date`, `category`.
  - Constraints: `range`, `values`, `unique`, `nullable`, `length`, `precision`.
  - Integration with Faker via `faker_template`.
  - Output to CSV or Excel.
- **Data Validator**:
  - Validate CSV/Excel data against a schema.
  - Checks: column existence, data types, value constraints, uniqueness, nullability, date formats.
  - Generate a report of invalid rows.
- **CLI**:
  - `etltest generate` command for data generation.
  - `etltest check` command for data validation.
- **Library**:
  - `DataGenerator` and `DataValidator` classes for programmatic use.
- **Testing**:
  - Comprehensive unit test suite with `pytest`.
  - High test coverage for core modules.
- **Documentation**:
  - `README.md` with installation and usage instructions.
  - Example `schema.yaml` file.
  - Docstrings for public functions and classes. 