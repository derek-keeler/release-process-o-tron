# Release Process-O-Tron

Generate hierarchical work items for your upcoming release, and see the state of the release throughout its duration.

Release Process-O-Tron is a command-line tool that generates structured JSON files containing work items for software releases, including code quality, testing, packaging, documentation, and publication tasks.

## Quick Start

```bash
# Install
pip install -e .

# Run
relprocotron --release-name "v1.0.0" --release-tag "v1.0.0" --release-type "dev" --release-date "2025-01-20" --project-url "https://github.com/user/repo" --software-name "MyApp" --software-version "1.0.0" --output-file "release.json"
```

For development setup and contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).
