---
title: 'ETLForge: A unified framework for synthetic test-data generation and ETL validation'
tags:
  - Python
  - ETL
  - data validation
  - synthetic data
  - data quality
  - testing
authors:
  - given-names: Kyriakos
    surname: Kartas
    orcid: 0009-0001-6477-4676
    affiliation: 1
affiliations:
  - name: Independent Researcher
    index: 1
date: 18 July 2024
bibliography: paper.bib
paper_type: software
version: 1.0.3
---

## Summary

ETLForge is a lightweight Python package (Python ≥ 3.9) that generates realistic synthetic test data *and* validates ETL outputs using the **same declarative schema**. One YAML/JSON file describes field types, ranges, uniqueness, nullability and optional Faker templates [@Faker2024]. The schema is consumed by two high-level components: `DataGenerator` (creates CSV/Excel datasets) and `DataValidator` (checks pipeline outputs, returning row-level error reports). A Click-based CLI [@Click2023] mirrors the library API, enabling automation within CI/CD workflows [@Fowler2013]. ETLForge therefore removes duplicated specifications and closes gaps where data-quality regressions can slip through testing cycles.

## Statement of need

Extract-Transform-Load (ETL) processes are critical for data-driven organizations, but testing these pipelines remains challenging [@Kimball2013; @Kleppmann2017]. Current testing approaches suffer from a fundamental disconnect: synthetic test data generation and output validation require separate tool chains with independent schema definitions. This creates several documented problems:

1. **Schema drift**: When generation schemas diverge from validation rules, tests may pass while production data fails validation [@Redman2016].
2. **Maintenance overhead**: Duplicate schema definitions require synchronized updates, increasing development time and error potential [@Dasu2003].
3. **Testing gaps**: Inconsistent test data may not exercise edge cases that production validation catches, leading to false confidence [@Loshin2010].

Existing libraries focus on either data generation (e.g., *Faker* [@Faker2024]) or validation (e.g., *Great Expectations* [@GreatExpectations2023], *pandera* [@Pandera2023]). Because these tools are independent, engineers must maintain **parallel schemas**—one for generation, one for validation—leading to drift and missed bugs. ETLForge unifies both stages under a single source of truth, reducing maintenance effort and improving test robustness. Its small dependency footprint (six runtime packages) fits comfortably inside continuous-integration pipelines.

## State of the field

The landscape of data generation and validation tools shows clear specialization but lacks integration:

| Capability | ETLForge | Faker | Great Expectations | pandera | Cerberus |
|------------|----------|-------|-------------------|---------|----------|
| Schema-driven generation | Yes | Manual scripting | No | No | No |
| Schema-driven validation | Yes | No | Yes | Yes | Yes |
| Single schema for both   | Yes | No | No | No | No |
| CLI & Python API         | Both | CLI only | Both | Python only | Python only |
| YAML/JSON schema support | Yes | No | Python/YAML | Python only | Python only |
| Lightweight dependencies | Yes (6 core) | Yes (1 core) | No (20+ deps) | Yes (5 core) | Yes (0 core) |

**Performance characteristics**: ETLForge generates 10,000 rows in ~6 seconds and validates 100,000 rows in ~2 seconds on standard hardware, making it suitable for CI/CD integration where Great Expectations may be too heavyweight for simple validation tasks.

**Limitations compared to existing tools**: Unlike Great Expectations, ETLForge does not provide data profiling, drift detection, or advanced statistical validations. Unlike pandera, it lacks integration with type checkers and advanced pandas DataFrame validation. ETLForge prioritizes simplicity and schema consistency over advanced features.

To our knowledge, no existing open-source project provides an integrated, schema-first workflow covering both generation and validation with a unified configuration format.

## Software description

ETLForge implements a dual-purpose architecture where a single YAML/JSON schema drives both data generation and validation processes. The schema format supports common data types (integer, float, string, date, category), constraints (ranges, uniqueness, nullability), and realistic data generation via Faker integration.

**Core components:**
- `DataGenerator`: Creates synthetic datasets using pandas [@McKinney2010] and numpy [@Harris2020] for numerical operations
- `DataValidator`: Validates CSV/Excel files against schema rules, returning detailed error reports
- CLI interface: Enables command-line automation via Click [@Click2023]

**Integration approach**: Rather than replacing existing tools, ETLForge complements ETL testing workflows by ensuring test data and validation rules remain synchronized. It integrates with pandas-based pipelines and exports to common formats (CSV, Excel via openpyxl).

## Quality control

GitHub Actions run comprehensive checks on Python 3.9-3.11:

* **Unit tests** (`pytest`), achieving **77% line coverage** across 587 statements (`pytest --cov`)
  - CLI module: 67% coverage (31/95 statements missing)  
  - Generator module: 74% coverage (64/244 statements missing)
  - Validator module: 86% coverage (33/241 statements missing)
* **Static analysis** (`flake8`, `black --check`, `mypy`) with type checking
* **Integration testing** via end-to-end example (`example.py`) validating complete workflows
* **Performance benchmarks** tracking generation/validation speed regressions

All checks complete in under 90 seconds on Ubuntu runners, supporting rapid development cycles.

**Known limitations**: 
- Large datasets (>1M rows) may require memory optimization
- Complex nested data structures are not supported
- Advanced statistical validations require integration with specialized tools

## Availability

* **Source code:** https://github.com/kkartas/ETLForge (MIT licence)
* **Latest release:** v1.0.3 (PyPI: `pip install etl-forge`)
* **Documentation:** https://etlforge.readthedocs.io/
* **Platforms:** Linux, macOS, Windows; Python 3.9-3.11
* **Installation:** `pip install etl-forge` (optional `etl-forge[faker]` for enhanced data generation)

## References

