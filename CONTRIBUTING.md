# Contributing to Release Process-O-Tron

Thank you for your interest in contributing to Release Process-O-Tron! We welcome contributions from the community and appreciate your help in making this tool better.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Git
- A GitHub account

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/release-process-o-tron.git
   cd release-process-o-tron
   ```

3. **Install development dependencies**:
   ```bash
   pip install -e .[dev]
   ```

4. **Verify your setup**:
   ```bash
   # Run tests
   python -m pytest tests/ -v
   
   # Run linting
   python -m ruff check .
   
   # Run type checking
   python -m mypy .
   ```

### Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards below

3. **Run tests and linting**:
   ```bash
   # Run all tests
   python -m pytest tests/ -v
   
   # Run linting and auto-fix issues
   python -m ruff check . --fix
   
   # Format code
   python -m ruff format .
   
   # Run type checking
   python -m mypy .
   ```

4. **Test your changes manually**:
   ```bash
   # Test basic functionality
   relprocotron --release-name "Test" --release-tag "v1.0.0" --release-type "dev" \
     --release-date "2025-01-20" --project-url "https://github.com/test/test" \
     --software-name "Test" --software-version "1.0.0" --output-file "test.json"
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub

## Coding Standards

### Python Code Style

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Maximum line length: 120 characters
- Use double quotes for strings
- Use Google-style docstrings

### Code Quality Tools

We use the following tools to maintain code quality:

- **Ruff** - Linting and code formatting
- **MyPy** - Static type checking
- **Pytest** - Unit testing with coverage reporting

All tools are configured in `pyproject.toml` and must pass before merging.

### Testing

- Write unit tests for all new functionality
- Maintain or improve code coverage
- Test edge cases and error conditions
- Use descriptive test names that explain what is being tested

Example test structure:
```python
def test_feature_with_valid_input() -> None:
    """Test that feature works correctly with valid input."""
    # Arrange
    input_data = "valid input"
    
    # Act
    result = your_function(input_data)
    
    # Assert
    assert result == expected_output
```

## Project Structure

```
release-process-o-tron/
├── relprocotron/           # Main package
│   ├── __init__.py
│   ├── __main__.py         # CLI entry point
│   └── templates/          # Jinja2 templates
│       └── release_process_o_tron.j2.json
├── tests/                  # Test suite
│   ├── __init__.py
│   └── test_main.py
├── docs/                   # Documentation
├── pyproject.toml          # Project configuration
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── LICENSE
```

## Types of Contributions

### Bug Reports

When filing an issue, please include:
- Python version
- Operating system
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Any error messages

### Feature Requests

For new features:
- Describe the use case
- Explain why it would be valuable
- Provide examples if possible
- Consider backward compatibility

### Code Contributions

We welcome:
- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- Test coverage improvements

## Release Process

Releases are handled by project maintainers using the following process:

1. Update version in `pyproject.toml`
2. Update release notes
3. Create a git tag
4. Build and publish to PyPI
5. Create GitHub release

Contributors don't need to worry about version bumping or releases.

## Getting Help

If you need help or have questions:
- Check existing issues and discussions
- Create a new issue with the "question" label
- Reach out to maintainers

## Code of Conduct

Please note that this project is released with a [Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## License

By contributing to Release Process-O-Tron, you agree that your contributions will be licensed under the same license as the project (MIT License).