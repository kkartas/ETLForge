# Contributing to ETLForge

Thank you for your interest in contributing to ETLForge! This guide will help you get started quickly.

## Quick Start

1. **Fork and clone** the repository:
   ```bash
   git clone https://github.com/yourusername/etl-forge.git
   cd etl-forge
   git checkout -b feature/your-feature-name
   ```

2. **Set up development environment**:
   ```bash
   pip install -e ".[dev]"
   python -m pytest tests/  # Verify setup
   ```

3. **Make your changes** and ensure tests pass:
   ```bash
   black etl_forge/ tests/    # Format code
   pytest tests/ --cov       # Run tests with coverage
   ```

4. **Submit a pull request** with a clear description of your changes.

## What We're Looking For

**High Priority:**
- Bug fixes and performance improvements
- New data types (JSON, UUID, etc.)
- Enhanced validation rules
- Documentation and examples

**Standards:**
- Follow PEP 8 (automated with `black`)
- Add tests for new functionality
- Include docstrings for public APIs
- Use type hints where helpful

## Questions or Issues?

- **Bug reports**: Use GitHub Issues with clear reproduction steps
- **Feature requests**: Open an issue with detailed use cases
- **Questions**: Check existing issues or start a discussion

## Code of Conduct

By participating, you agree to uphold our [Code of Conduct](CODE_OF_CONDUCT.md).

---

Thank you for contributing to ETLForge! 🚀

 