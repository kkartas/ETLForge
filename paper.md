---
title: 'ETLForge: A Python Framework for Synthetic Test Data Generation and ETL Pipeline Validation'
tags:
  - Python
  - ETL
  - data validation
  - synthetic data
  - data quality
  - testing
  - data engineering
authors:
  - name: Kyriakos Kartas
    orcid: 0000-0000-0000-0000
    affiliation: 1
affiliations:
 - name: Independent Developer
   index: 1
date: 15 June 2025
bibliography: paper.bib
---

# Summary

Extract, Transform, Load (ETL) pipelines are fundamental to modern data infrastructure. Testing these pipelines is challenging, as production data may be sensitive or unavailable, and manually creating realistic test data is a significant bottleneck [@Kimball2013]. `ETLForge` is a Python framework that addresses these challenges by providing an integrated solution for schema-driven synthetic data generation and automated output validation. It allows data engineers and scientists to define data structures via a simple declarative schema and use it as a single source of truth for both creating test data and validating pipeline outputs, thereby improving the reliability and development velocity of data-intensive applications.

# Statement of need

The reliability of data-intensive systems depends on robust testing, yet the ecosystem for testing data pipelines remains fragmented. While numerous tools exist for parts of the problem, a lightweight, integrated solution is often missing.

Data generation tools like `Faker` [@Faker2024] are excellent for producing realistic-looking but structurally unaware data points. On the other end, data validation libraries like `pandera` [@Pandera2023] and `Great Expectations` [@GreatExpectations2023] provide powerful, dataframe-centric validation but do not assist in generating the input data needed for testing. This fragmentation forces developers to either use production data (which carries privacy and availability risks [@Redman2016]) or write bespoke, often complex, scripts to bridge the gap between generation and validation.

`Great Expectations` is a comprehensive data quality platform, offering automated data profiling, documentation, and a rich set of "expectations." However, its power comes with significant setup complexity and a dependency footprint that may be excessive for teams needing a lightweight, scriptable tool for CI/CD environments. `pandera` offers a more Pythonic, code-first approach to schema definition and validation, which is excellent for integration within Python applications, but it similarly does not have a built-in data generation capability based on its schemas.

`ETLForge` fills this specific gap by positioning the schema as the central artifact for both generation and validation. By defining a schema once in a simple YAML or JSON format, a developer can generate an arbitrarily large, structurally-correct dataset to test a pipeline, and then use that exact same schema to validate the pipeline's final output. This "schema-first" approach provides a single source of truth, simplifies the testing workflow, and reduces the friction of implementing robust data quality checks. It is designed to be a simple, lightweight, and easily scriptable tool that fits naturally into both local development loops and automated CI/CD testing pipelines without requiring extensive configuration.

# Core functionality

## Dual Interface Design

`ETLForge` provides both programmatic and command-line interfaces built with `Click` [@click2022] to support different workflow preferences:

```python
# Library usage
# Implementation

`ETLForge` is implemented in Python 3.8+ using modern software engineering practices:

- **Core dependencies**: `pandas` [@McKinney2010] for data manipulation, `PyYAML` [@pyyaml2021] for schema parsing, and `Click` [@click2022] for the CLI.
- **Optional integrations**: `Faker` [@Faker2024] for realistic data generation, `openpyxl` for Excel support.
- **Architecture**: The framework features a modular design with distinct `DataGenerator` and `DataValidator` components. This separation of concerns allows each component to be used independently and facilitates extensibility.
- **Testing**: A comprehensive test suite using `pytest` provides high code coverage (>95%), ensuring reliability.
- **Documentation**: User-friendly HTML documentation is generated using `Sphinx`.

# Research Applications

`ETLForge` is a valuable tool for the research community, particularly in computational fields:

- **Reproducibility**: Researchers can package an `ETLForge` schema with their code, allowing others to generate an identical data structure for reproducing pipeline results without sharing potentially sensitive raw data.
- **Algorithm Benchmarking**: The data generator can be used to create controlled datasets of varying size and complexity to benchmark the performance and scalability of data processing algorithms.
- **Educational Tool**: The framework serves as a practical tool for teaching data engineering and data quality principles, allowing students to experiment with pipeline testing in a controlled environment.

# Comparison with existing tools

| Feature | ETLForge | Faker [@Faker2024] | Great Expectations [@GreatExpectations2023] | pandera [@Pandera2023] |
|---|---|---|---|---|
| **Schema-Driven Generation** | ✅ | ❌ | ❌ | ❌ |
| **Integrated Validation** | ✅ | ❌ | ✅ | ✅ |
| **Unified Gen/Validate Schema** | ✅ | ❌ | ❌ | ❌ |
| **Lightweight & Scriptable** | ✅ | ✅ | ❌ | ✅ |
| CLI Interface | ✅ | ✅ | ✅ | ❌ |
| Declarative YAML/JSON Schema | ✅ | ❌ | ✅ | ❌ |

`ETLForge` uniquely combines generation and validation in a single, lightweight framework specifically designed for ETL testing workflows.

# Conclusion

`ETLForge` provides an integrated, schema-first solution for the critical but often fragmented tasks of test data generation and validation. By unifying these processes around a single, declarative schema, it lowers the barrier to implementing robust testing practices in data-intensive projects. Its lightweight design and dual library/CLI interface make it a flexible tool for both local development and automated CI/CD workflows, addressing a clear gap in the existing open-source data ecosystem.

# Acknowledgements

We acknowledge the developers and communities behind the open-source libraries that `ETLForge` is built upon, including `pandas`, `numpy`, `PyYAML`, `Click`, and `Faker`. Their contributions are fundamental to this work.

# References

# Future development

Planned enhancements include: 