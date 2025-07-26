# Release Process-O-Tron

Generate hierarchical work items for your upcoming release, and see the state of the release throughout its duration.

Release Process-O-Tron is a command-line tool that helps software teams organize and track their release processes. It generates structured JSON files containing hierarchical work items (tasks) for different phases of a software release, including code quality checks, testing, package building, documentation updates, and publication. The tool can also create GitHub issues directly from the generated work items.

## Installation

```bash
# Clone the repository
git clone https://github.com/derek-keeler/release-process-o-tron.git
cd release-process-o-tron

# Install Python dependencies
pip install -e .

# Verify installation
relprocotron --help
```

## Example Usage

To generate a JSON file of work items for your release:

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

## Development

For development setup, testing, and contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).
