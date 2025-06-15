# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-15

### Changed
- **BREAKING**: Migrated packaging to `pyproject.toml` from `setup.py`.
- Updated project version to `1.0.0` for stable release.
- Revised `paper.md` with a more rigorous "Statement of Need" and added new citations.
- Improved user-facing error handling to be more informative.
- Added comprehensive docstrings to all public methods.
- Added placeholder badges for build status, coverage, and license to `README.md`.
- Set up Sphinx for HTML documentation generation.

### Added
- `pyproject.toml` for modern Python packaging.
- `pandera` and `Great Expectations` citations to `paper.bib`.
- Sphinx configuration (`docs/`) and `.readthedocs.yaml` for automated documentation builds.
- More tests for failure conditions to increase coverage.

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