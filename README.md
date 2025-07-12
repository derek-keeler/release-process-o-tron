# Release Process-O-Tron

Generate hierarchical work items for your upcoming release, and see the state of the release throughout its duration.

## Overview

Release Process-O-Tron is a command-line tool that helps software teams organize and track their release processes. It generates structured JSON files containing hierarchical work items (tasks) for different phases of a software release, including:

- **Code Quality Checks** - Linting, type checking, and other quality assurance tasks
- **Testing** - Unit tests, integration tests, and cross-platform compatibility testing
- **Package Building** - Creating source distributions, wheels, and validating packages
- **Documentation Updates** - Version updates, README maintenance, and release notes
- **Release Preparation** - Git tagging, artifact creation, and release preparation
- **Publication** - Publishing to PyPI, GitHub releases, and other distribution channels

The tool supports different release types (LTS, dev, experimental, early-access) and can generate GitHub issues directly from the structured work items.

## Features

- ✅ Generate structured release task hierarchies
- ✅ Support for multiple release types (LTS, dev, experimental, early-access)
- ✅ Export to JSON format for integration with other tools
- ✅ Create GitHub issues directly from generated tasks
- ✅ Customizable with comments and metadata
- ✅ Cross-platform support (Windows, Linux, macOS)

## Quick Start

### Prerequisites

- Python 3.12 or higher
- pip package manager

### Installation

#### Linux/macOS

```bash
# Clone the repository
git clone https://github.com/derek-keeler/release-process-o-tron.git
cd release-process-o-tron

# Install Python dependencies
pip install -e .

# Verify installation
relprocotron --help
```

#### Windows

```powershell
# Clone the repository
git clone https://github.com/derek-keeler/release-process-o-tron.git
cd release-process-o-tron

# Install Python dependencies
pip install -e .

# Verify installation
relprocotron --help
```

### Generating a Release JSON File

To produce a JSON file of work items for your release:

```bash
relprocotron \
  --release-name "My Project v2.1.0" \
  --release-tag "v2.1.0" \
  --release-type "LTS" \
  --release-date "2025-02-15" \
  --project-url "https://github.com/myorg/myproject" \
  --software-name "My Project" \
  --software-version "2.1.0" \
  --output-file "release-v2.1.0.json"
```

#### Parameters

- `--release-name`: Human-readable name for the release
- `--release-tag`: Git tag that will be created for the release
- `--release-type`: Type of release (LTS, dev, experimental, early-access)
- `--release-date`: Release date in YYYY-MM-DD format
- `--project-url`: URL of the project repository
- `--software-name`: Name of the software being released
- `--software-version`: Version of the software being released
- `--output-file`: Path where the JSON file will be saved

#### Optional Parameters

- `--comment`: Add additional comments (can be used multiple times)
- `--dry-run`: Perform a dry run without making actual changes
- `--verbose`: Enable verbose logging

### Creating GitHub Issues

You can also create GitHub issues directly from a generated JSON file:

```bash
relprocotron \
  --create-issues \
  --input-file "release-v2.1.0.json" \
  --github-repo "myorg/myproject" \
  --github-token "your-github-token" \
  --dry-run
```

## Example Output

The generated JSON file contains a structured hierarchy like this:

```json
{
  "release": {
    "name": "My Project v2.1.0",
    "tag": "v2.1.0",
    "type": "LTS",
    "date": "2025-02-15",
    "project_url": "https://github.com/myorg/myproject",
    "software_name": "My Project",
    "software_version": "2.1.0"
  },
  "tasks": [
    {
      "title": "Pre-Release Code Quality",
      "description": ["Ensure code quality standards are met before release"],
      "project": "My Project",
      "tags": ["quality", "pre-release"],
      "category": "Infrastructure",
      "priority": 1,
      "children": [
        {
          "title": "Run Linting",
          "description": ["Execute ruff linting checks"],
          "project": "My Project",
          "tags": ["linting", "ruff"],
          "category": "Code Quality",
          "priority": 1
        }
      ]
    }
  ]
}
```
