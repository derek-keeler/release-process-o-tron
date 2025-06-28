# GitHub Actions PR Workflow

This repository includes a comprehensive GitHub Actions workflow for PR validation that ensures code quality and functionality.

## Workflow Features

The PR validation workflow (`.github/workflows/pr-validation.yml`) includes:

### Cross-Platform Testing
- **Ubuntu Latest** and **Windows Latest**
- **Python 3.12** as the primary runtime

### Code Quality Checks
- **Ruff** - Modern Python linter with comprehensive rule set
- **MyPy** - Static type checking for Python
- **Pytest** - Unit testing with coverage reporting

### Package Building
- **Build** - Creates source and wheel distributions
- **Twine** - Validates package metadata for PyPI compatibility
- **Artifacts** - Uploads build artifacts for inspection

### Coverage Reporting
- **Codecov** integration for coverage tracking
- **Coverage reports** in HTML, terminal, and XML formats

## Local Development

To run the same checks locally:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run linting
ruff check

# Run type checking
mypy

# Run tests with coverage
pytest --cov

# Build package
python -m build
```

## Workflow Triggers

The workflow runs on:
- Pull requests to the `main` branch
- Manual dispatch via GitHub Actions UI

## Test Coverage

The test suite covers:
- CLI help functionality
- Required argument validation
- Valid argument processing
- Dry-run flag behavior
- Multiple comment handling
- Invalid input rejection

Current coverage: **96%** of the main module