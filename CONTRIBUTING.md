# Contributing to ETLForge

Thank you for your interest in contributing to ETLForge! This guide will help you get started quickly and effectively contribute to our unified data generation and validation framework.

## Quick Start

1. **Fork and clone** the repository:
   ```bash
   git clone https://github.com/yourusername/etl-forge.git
   cd etl-forge
   git checkout -b feature/your-feature-name
   ```

2. **Set up development environment**:
   ```bash
   # Install with all development dependencies
   pip install -e ".[dev,faker]"
   
   # Verify setup works
   pytest tests/  
   python example.py  # Run end-to-end example
   ```

3. **Make your changes** and ensure quality standards:
   ```bash
   # Format code (required)
   black etl_forge/ tests/
   
   # Run linting (required)
   flake8 etl_forge/ tests/
   
   # Type checking (recommended)
   mypy etl_forge/
   
   # Run tests with coverage (required)
   pytest tests/ --cov=etl_forge --cov-report=term-missing
   ```

4. **Submit a pull request** with:
   - Clear description of changes and motivation
   - Test coverage for new functionality
   - Updated documentation if needed
   - Reference to related issues

## Development Guidelines

### Code Standards
- **PEP 8 compliance** (automated with `black`)
- **Type hints** for all public APIs and complex functions
- **Docstrings** following Google style for all public functions/classes
- **Error handling** with meaningful error messages
- **Backward compatibility** maintained unless major version bump

### Testing Requirements
- **Unit tests** for all new functionality (aim for >85% coverage)
- **Integration tests** for end-to-end workflows
- **Error case testing** for edge conditions and invalid inputs
- **Performance tests** for generation/validation speed regressions

### Documentation Standards
- **API documentation** updated for public interface changes
- **README.md** updated for new features or installation changes
- **Example code** provided for significant new functionality
- **Docstring examples** for complex functions

## What We're Looking For

### High Priority Contributions
- **Bug fixes** with reproduction cases and tests
- **Performance improvements** with benchmarks
- **New data types** (JSON, UUID, custom patterns)
- **Enhanced validation rules** (statistical checks, cross-field validation)
- **Integration examples** with popular ETL frameworks
- **Documentation improvements** and tutorials

### Medium Priority
- **CLI enhancements** (new commands, better error messages)
- **Schema format extensions** (inheritance, templates)
- **Export format support** (Parquet, JSON, XML)
- **Internationalization** for error messages

### Architecture Considerations
- **Maintain single-schema principle** - both generation and validation must use same schema
- **Keep dependencies minimal** - avoid heavy dependencies that impact CI/CD performance
- **Preserve backward compatibility** - schema format and API stability is crucial
- **Performance-conscious** - maintain sub-second generation and validation for CI/CD use

## Testing Your Changes

### Local Testing
```bash
# Run full test suite
pytest tests/ -v

# Test with multiple Python versions (if available)
tox

# Run performance benchmarks
python benchmark.py

# Test example workflows
python example.py
```

### Integration Testing
```bash
# Test CLI functionality
python -m etl_forge.cli generate --schema tests/fixtures/simple_schema.yaml --rows 100 --output test.csv
python -m etl_forge.cli check --input test.csv --schema tests/fixtures/simple_schema.yaml
```

## Reporting Issues

### Bug Reports
Please include:
- **Python version** and operating system
- **ETLForge version** (`pip show etl-forge`)
- **Minimal reproduction case** with schema and data samples
- **Expected vs actual behavior**
- **Complete error traceback**

### Feature Requests
Please provide:
- **Clear use case** description with real-world examples
- **Proposed API** or interface design
- **Relationship to existing features**
- **Impact on schema format** (if any)

### Security Issues
Report security vulnerabilities privately to: [mail@kkartas.gr](mailto:mail@kkartas.gr)

## Release Process

### Versioning
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes to API or schema format
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, documentation updates

### Release Checklist
- [ ] All tests pass on Python 3.9-3.11
- [ ] Coverage remains >75%
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in `etl_forge/__init__.py`
- [ ] GitHub release created with notes

## Community Standards

### Code of Conduct
By participating, you agree to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). We are committed to providing a welcoming and inclusive environment for all contributors.

### Communication Channels
- **GitHub Issues**: Bug reports, feature requests, general discussion
- **GitHub Discussions**: Questions, ideas, community feedback
- **Pull Requests**: Code reviews and technical discussion

## Recognition

Contributors are recognized in:
- **README.md**: All contributors listed
- **CHANGELOG.md**: Credit for specific contributions
- **Releases**: Acknowledgment in release notes

---

Thank you for contributing to ETLForge! Together we're making ETL testing more reliable and maintainable. 🚀

 