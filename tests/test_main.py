"""Tests for the main CLI module."""

import json
from pathlib import Path

from click.testing import CliRunner

from relprocotron.__main__ import main


def test_main_help() -> None:
    """Test that the main command shows help when called with --help."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "Release Process-O-Tron CLI tool" in result.output
    assert "--release-name" in result.output
    assert "--release-tag" in result.output
    assert "--release-type" in result.output
    assert "--output-file" in result.output


def test_main_with_dry_run() -> None:
    """Test that the main command writes file regardless of dry-run flag."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            main,
            [
                "--release-name",
                "Test Release",
                "--release-tag",
                "v1.0.0",
                "--release-type",
                "LTS",
                "--release-date",
                "2025-01-20",
                "--project-url",
                "https://github.com/test/test",
                "--software-name",
                "Test Software",
                "--software-version",
                "1.0.0",
                "--dry-run",
                "--output-file",
                "dry_run_output.json",
            ],
        )

        assert result.exit_code == 0

        # Verify JSON file was created even in dry run mode
        assert Path("dry_run_output.json").exists()


def test_main_with_comments() -> None:
    """Test that the main command handles multiple comments."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            main,
            [
                "--release-name",
                "Test Release",
                "--release-tag",
                "v1.0.0",
                "--release-type",
                "experimental",
                "--release-date",
                "2025-01-20",
                "--project-url",
                "https://github.com/test/test",
                "--software-name",
                "Test Software",
                "--software-version",
                "1.0.0",
                "--comment",
                "First comment",
                "--comment",
                "Second comment",
                "--output-file",
                "comments_output.json",
            ],
        )

        assert result.exit_code == 0

        # Verify JSON file contains comments
        with Path("comments_output.json").open("r", encoding="utf-8") as f:
            data = json.load(f)
        assert "comments" in data["release"]
        assert data["release"]["comments"] == ["First comment", "Second comment"]


def test_json_structure_dev_release() -> None:
    """Test that generated JSON has correct structure for dev release."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            main,
            [
                "--release-name",
                "Dev Release",
                "--release-tag",
                "v1.0.0-dev",
                "--release-type",
                "dev",
                "--release-date",
                "2025-01-20",
                "--project-url",
                "https://github.com/test/test",
                "--software-name",
                "Test App",
                "--software-version",
                "1.0.0",
                "--output-file",
                "dev_release.json",
            ],
        )

        assert result.exit_code == 0

        # Parse and validate JSON structure
        with Path("dev_release.json").open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Verify release metadata
        assert "release" in data
        assert data["release"]["name"] == "Dev Release"
        assert data["release"]["tag"] == "v1.0.0-dev"
        assert data["release"]["type"] == "dev"

        # Verify tasks structure
        assert "tasks" in data
        assert isinstance(data["tasks"], list)
        assert len(data["tasks"]) > 0

        # Verify each task has required fields
        for task in data["tasks"]:
            assert "title" in task
            assert "description" in task
            assert "project" in task
            assert "tags" in task
            assert "category" in task
            assert "priority" in task
            assert isinstance(task["description"], list)
            assert isinstance(task["tags"], list)
            assert isinstance(task["priority"], int)

            # Check children tasks if they exist
            if "children" in task:
                for child in task["children"]:
                    assert "title" in child
                    assert "description" in child
                    assert "project" in child
                    assert "tags" in child
                    assert "category" in child
                    assert "priority" in child


def test_create_issues_dry_run() -> None:
    """Test that create-issues command works with dry run."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # First generate a JSON file
        result = runner.invoke(
            main,
            [
                "--release-name",
                "Test Release",
                "--release-tag",
                "v1.0.0",
                "--release-type",
                "LTS",
                "--release-date",
                "2025-01-20",
                "--project-url",
                "https://github.com/test/test",
                "--software-name",
                "Test Software",
                "--software-version",
                "1.0.0",
                "--output-file",
                "test_release.json",
            ],
        )

        assert result.exit_code == 0
        assert Path("test_release.json").exists()

        # Now test create-issues with dry run
        result = runner.invoke(
            main,
            [
                "--create-issues",
                "--input-file",
                "test_release.json",
                "--github-repo",
                "test/test",
                "--github-token",
                "dummy-token",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "DRY RUN: No actual issues will be created" in result.output
        assert "Successfully created 0 issues" in result.output


def test_create_issues_missing_parameters() -> None:
    """Test that create-issues command fails with missing parameters."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Test with missing input file
        result = runner.invoke(
            main,
            [
                "--create-issues",
                "--github-repo",
                "test/test",
                "--github-token",
                "dummy-token",
            ],
        )

        assert result.exit_code != 0
        assert "Missing required options for issue creation" in result.output


def test_json_structure_lts_release() -> None:
    """Test that generated JSON includes publication tasks for LTS release."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            main,
            [
                "--release-name",
                "LTS Release",
                "--release-tag",
                "v2.0.0",
                "--release-type",
                "LTS",
                "--release-date",
                "2025-01-20",
                "--project-url",
                "https://github.com/test/test",
                "--software-name",
                "Test App",
                "--software-version",
                "2.0.0",
                "--output-file",
                "lts_release.json",
            ],
        )

        assert result.exit_code == 0

        # Parse and validate JSON structure
        with Path("lts_release.json").open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Verify publication task exists for LTS release
        task_titles = [task["title"] for task in data["tasks"]]
        assert "Publication" in task_titles


def test_json_validity_all_release_types() -> None:
    """Test that generated JSON is valid for all supported release types."""
    runner = CliRunner()
    release_types = ["dev", "LTS", "experimental", "early-access"]

    for release_type in release_types:
        with runner.isolated_filesystem():
            # Test basic release generation
            result = runner.invoke(
                main,
                [
                    "--release-name",
                    f"{release_type.title()} Release",
                    "--release-tag",
                    f"v1.0.0-{release_type.lower()}",
                    "--release-type",
                    release_type,
                    "--release-date",
                    "2025-01-20",
                    "--project-url",
                    "https://github.com/test/test",
                    "--software-name",
                    "Test App",
                    "--software-version",
                    "1.0.0",
                    "--output-file",
                    f"{release_type}_release.json",
                ],
            )

            assert result.exit_code == 0, f"CLI failed for release type: {release_type}"

            # Validate JSON is syntactically correct
            json_file = Path(f"{release_type}_release.json")
            assert json_file.exists(), f"JSON file not created for release type: {release_type}"

            with json_file.open("r", encoding="utf-8") as f:
                content = f.read()
                assert content.strip(), f"JSON file is empty for release type: {release_type}"

                # Validate JSON can be parsed without errors
                try:
                    data = json.loads(content)
                except json.JSONDecodeError as e:
                    raise AssertionError(f"Invalid JSON generated for release type {release_type}: {e}") from e

                # Validate JSON can be re-serialized (round-trip test)
                try:
                    re_serialized = json.dumps(data, indent=2)
                    re_parsed = json.loads(re_serialized)
                    assert isinstance(re_parsed, dict), f"JSON structure invalid for release type: {release_type}"
                except (TypeError, ValueError) as e:
                    raise AssertionError(f"JSON round-trip failed for release type {release_type}: {e}") from e


def test_json_validity_with_comments() -> None:
    """Test that generated JSON is valid when comments are included."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Test with multiple comments
        result = runner.invoke(
            main,
            [
                "--release-name",
                "Commented Release",
                "--release-tag",
                "v1.0.0",
                "--release-type",
                "dev",
                "--release-date",
                "2025-01-20",
                "--project-url",
                "https://github.com/test/test",
                "--software-name",
                "Test App",
                "--software-version",
                "1.0.0",
                "--comment",
                "First comment with special chars: áéíóú",
                "--comment",
                'Second comment with quotes and "escapes"',
                "--comment",
                "Third comment with newlines\nand\ttabs",
                "--output-file",
                "commented_release.json",
            ],
        )

        assert result.exit_code == 0

        # Validate JSON with complex comment content
        with Path("commented_release.json").open("r", encoding="utf-8") as f:
            content = f.read()

            # Validate JSON parsing
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                raise AssertionError(f"Invalid JSON generated with comments: {e}") from e

            # Validate comments are properly escaped and included
            assert "comments" in data["release"]
            assert len(data["release"]["comments"]) == 3
            assert "áéíóú" in data["release"]["comments"][0]
            assert '"escapes"' in data["release"]["comments"][1]
            assert "\n" in data["release"]["comments"][2]


def test_json_structure_consistency() -> None:
    """Test that JSON structure is consistent and contains required fields."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            main,
            [
                "--release-name",
                "Structure Test",
                "--release-tag",
                "v1.0.0",
                "--release-type",
                "LTS",
                "--release-date",
                "2025-01-20",
                "--project-url",
                "https://github.com/test/test",
                "--software-name",
                "Test App",
                "--software-version",
                "1.0.0",
                "--output-file",
                "structure_test.json",
            ],
        )

        assert result.exit_code == 0

        with Path("structure_test.json").open("r", encoding="utf-8") as f:
            data = json.load(f)

            # Validate top-level structure
            assert isinstance(data, dict), "Root JSON element must be an object"
            assert "release" in data, "JSON must contain 'release' section"
            assert "tasks" in data, "JSON must contain 'tasks' section"

            # Validate release section
            release = data["release"]
            required_release_fields = [
                "name",
                "tag",
                "type",
                "date",
                "project_url",
                "software_name",
                "software_version",
            ]
            for field in required_release_fields:
                assert field in release, f"Release section missing required field: {field}"
                assert isinstance(release[field], str), f"Release field '{field}' must be a string"

            # Validate tasks section
            tasks = data["tasks"]
            assert isinstance(tasks, list), "Tasks must be a list"
            assert len(tasks) > 0, "Must have at least one task"

            # Validate each task structure
            for i, task in enumerate(tasks):
                assert isinstance(task, dict), f"Task {i} must be an object"
                required_task_fields = ["title", "description", "project", "tags", "category", "priority"]
                for field in required_task_fields:
                    assert field in task, f"Task {i} missing required field: {field}"

                # Validate field types
                assert isinstance(task["title"], str), f"Task {i} title must be a string"
                assert isinstance(task["description"], list), f"Task {i} description must be a list"
                assert isinstance(task["project"], str), f"Task {i} project must be a string"
                assert isinstance(task["tags"], list), f"Task {i} tags must be a list"
                assert isinstance(task["category"], str), f"Task {i} category must be a string"
                assert isinstance(task["priority"], int), f"Task {i} priority must be an integer"

                # Validate children structure if present
                if "children" in task:
                    assert isinstance(task["children"], list), f"Task {i} children must be a list"
                    for j, child in enumerate(task["children"]):
                        assert isinstance(child, dict), f"Task {i} child {j} must be an object"
                        for field in required_task_fields:
                            assert field in child, f"Task {i} child {j} missing required field: {field}"


def test_priority_field_in_generated_json() -> None:
    """Test that priority field is included in generated JSON tasks."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            main,
            [
                "--release-name",
                "Priority Test",
                "--release-tag",
                "v1.0.0",
                "--release-type",
                "dev",
                "--release-date",
                "2025-01-20",
                "--project-url",
                "https://github.com/test/test",
                "--software-name",
                "Test App",
                "--software-version",
                "1.0.0",
                "--output-file",
                "priority_test.json",
            ],
        )

        assert result.exit_code == 0

        # Parse and validate priority fields
        with Path("priority_test.json").open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Check that all tasks have priority field
        for task in data["tasks"]:
            assert "priority" in task, f"Task '{task['title']}' missing priority field"
            assert isinstance(task["priority"], int), f"Task '{task['title']}' priority must be integer"
            assert task["priority"] > 0, f"Task '{task['title']}' priority must be positive"

            # Check children tasks if they exist
            if "children" in task:
                for child in task["children"]:
                    assert "priority" in child, f"Child task '{child['title']}' missing priority field"
                    assert isinstance(child["priority"], int), f"Child task '{child['title']}' priority must be integer"
                    assert child["priority"] > 0, f"Child task '{child['title']}' priority must be positive"

        # Check that tasks are in different priority groups
        priorities = [task["priority"] for task in data["tasks"]]
        assert len(set(priorities)) > 1, "Tasks should have different priorities for ordering"
