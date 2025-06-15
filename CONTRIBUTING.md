# Contributing to ETLTest

We welcome contributions to ETLTest! This document provides guidelines and information about contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/etltest.git
   cd etltest
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip or conda for package management
- Git for version control

### Installation

1. **Install the package in development mode:**
   ```bash
   pip install -e .
   ```

2. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```
   
   Or install manually:
   ```bash
   pip install pytest pytest-cov black flake8 mypy
   ```

3. **Verify installation:**
   ```bash
   python -m pytest tests/
   ```

## How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **Bug reports and fixes**
- **Feature requests and implementations**
- **Documentation improvements**
- **Performance optimizations**
- **Test coverage improvements**
- **Examples and tutorials**

### Priority Areas

We're particularly interested in contributions in these areas:

- **New data types**: Support for additional data types (JSON, UUID, etc.)
- **Enhanced constraints**: More sophisticated validation rules
- **Performance improvements**: Optimization for large datasets
- **Integration plugins**: Connectors for popular ETL tools
- **Documentation**: Examples, tutorials, and API documentation

## Coding Standards

### Python Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use type hints where appropriate
- Write docstrings for all public functions and classes

### Code Quality Tools

Before submitting, ensure your code passes:

```bash
# Code formatting
black etltest/ tests/

# Linting
flake8 etltest/ tests/

# Type checking (optional but recommended)
mypy etltest/

# Tests
pytest tests/ --cov=etltest
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `DataGenerator`)
- **Functions/Variables**: snake_case (e.g., `generate_data`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_ROWS`)
- **Private methods**: Leading underscore (e.g., `_generate_column`)

## Testing

### Writing Tests

- Write tests for all new functionality
- Maintain or improve test coverage
- Use descriptive test names
- Include both positive and negative test cases
- Test edge cases and error conditions

### Test Structure

```python
class TestYourFeature:
    def setup_method(self):
        """Set up test fixtures."""
        # Setup code here
    
    def test_normal_case(self):
        """Test the normal/expected behavior."""
        # Test implementation
    
    def test_edge_case(self):
        """Test edge cases."""
        # Test implementation
    
    def test_error_handling(self):
        """Test error conditions."""
        # Test implementation
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=etltest --cov-report=html

# Run specific test file
pytest tests/test_generator.py

# Run specific test
pytest tests/test_generator.py::TestDataGenerator::test_generate_data
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def generate_data(self, num_rows: int) -> pd.DataFrame:
    """
    Generate synthetic data based on the loaded schema.
    
    Args:
        num_rows: Number of rows to generate
        
    Returns:
        pd.DataFrame: Generated data
        
    Raises:
        ValueError: If no schema is loaded
        
    Example:
        >>> generator = DataGenerator('schema.yaml')
        >>> df = generator.generate_data(100)
        >>> len(df)
        100
    """
```

### README Updates

- Update the README.md if your changes affect:
  - Installation instructions
  - Usage examples
  - Feature descriptions
  - API documentation

## Submitting Changes

### Pull Request Process

1. **Ensure tests pass:**
   ```bash
   pytest tests/
   ```

2. **Update documentation** as needed

3. **Add entries to CHANGELOG** (if applicable)

4. **Submit pull request** with:
   - Clear, descriptive title
   - Detailed description of changes
   - Reference to related issues
   - Screenshots/examples if applicable

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass
- [ ] New tests added
- [ ] Coverage maintained/improved

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings introduced
```

### Review Process

- All submissions require review
- Reviews focus on:
  - Code quality and style
  - Test coverage
  - Documentation completeness
  - Backward compatibility
  - Performance implications

## Issue Reporting

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Update to latest version** to see if issue persists
3. **Check documentation** for known limitations

### Issue Template

```markdown
## Bug Report / Feature Request

**Description:**
Clear description of the issue or feature

**Expected Behavior:**
What you expected to happen

**Actual Behavior:**
What actually happened

**Environment:**
- ETLTest version:
- Python version:
- Operating System:
- Dependencies versions:

**Reproducible Example:**
```python
# Minimal code example
```

**Additional Context:**
Any other relevant information
```

### Priority Labels

Issues are labeled by priority:
- **critical**: Security vulnerabilities, data corruption
- **high**: Significant functionality broken
- **medium**: Important features not working as expected
- **low**: Minor issues, enhancements

## Development Workflow

### Git Workflow

1. **Keep your fork updated:**
   ```bash
   git remote add upstream https://github.com/original/etltest.git
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create feature branches:**
   ```bash
   git checkout -b feature/descriptive-name
   ```

3. **Make atomic commits:**
   ```bash
   git add specific-files
   git commit -m "Clear, descriptive message"
   ```

4. **Push and create PR:**
   ```bash
   git push origin feature/descriptive-name
   ```

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add support for UUID data type

- Implement UUID field type in generator
- Add validation for UUID format
- Include tests and documentation
- Closes #123
```

**Format:**
- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation changes
- `test:` test additions/modifications
- `refactor:` code refactoring
- `perf:` performance improvements

## Questions and Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: [maintainer-email] for private matters

## Recognition

Contributors are recognized in:
- GitHub contributors list
- CHANGELOG.md for significant contributions
- Documentation acknowledgments

Thank you for contributing to ETLTest! 