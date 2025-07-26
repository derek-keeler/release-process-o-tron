"""Tests for the main CLI module."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from relprocotron.__main__ import GitHubClient, _collect_all_tags, _validate_repository_labels, main


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


def test_collect_all_tags() -> None:
    """Test that _collect_all_tags correctly extracts all unique tags from JSON data."""
    # Test data with various tag configurations
    test_data = {
        "tasks": [
            {
                "title": "Task 1",
                "tags": ["tag1", "tag2"],
                "children": [
                    {"title": "Child 1", "tags": ["tag3", "tag1"]},  # tag1 is duplicate
                    {"title": "Child 2", "tags": ["tag4"]},
                ],
            },
            {
                "title": "Task 2",
                "tags": ["tag2", "tag5"],  # tag2 is duplicate
                "children": [
                    {"title": "Child 3", "tags": []},  # empty tags
                ],
            },
            {
                "title": "Task 3",
                "tags": ["tag6"],
                # no children
            },
        ]
    }

    result = _collect_all_tags(test_data)
    expected = {"tag1", "tag2", "tag3", "tag4", "tag5", "tag6"}
    assert result == expected


def test_collect_all_tags_empty_data() -> None:
    """Test _collect_all_tags with empty or missing data."""
    # Empty tasks
    assert _collect_all_tags({"tasks": []}) == set()

    # Missing tasks key
    assert _collect_all_tags({}) == set()

    # Tasks with no tags
    test_data = {
        "tasks": [
            {"title": "Task 1"},  # missing tags key
            {"title": "Task 2", "tags": []},  # empty tags
        ]
    }
    assert _collect_all_tags(test_data) == set()


def test_validate_repository_labels_success() -> None:
    """Test _validate_repository_labels when all tags exist as labels."""
    # Mock GitHub client
    mock_client = Mock(spec=GitHubClient)
    mock_client.list_labels.return_value = [
        {"name": "tag1", "description": "Tag 1"},
        {"name": "tag2", "description": "Tag 2"},
        {"name": "tag3", "description": "Tag 3"},
    ]
    mock_client.repo = "test/repo"

    # Test with tags that all exist
    required_tags = {"tag1", "tag2"}

    # Should not raise exception
    _validate_repository_labels(mock_client, required_tags)

    # Verify labels were fetched
    mock_client.list_labels.assert_called_once()


def test_validate_repository_labels_missing_tags() -> None:
    """Test _validate_repository_labels when some tags don't exist as labels."""
    # Mock GitHub client
    mock_client = Mock(spec=GitHubClient)
    mock_client.list_labels.return_value = [
        {"name": "tag1", "description": "Tag 1"},
        {"name": "tag2", "description": "Tag 2"},
    ]
    mock_client.repo = "test/repo"

    # Test with tags where some don't exist
    required_tags = {"tag1", "tag2", "tag3", "tag4"}

    # Should raise ClickException
    with pytest.raises(Exception) as exc_info:
        _validate_repository_labels(mock_client, required_tags)

    error_message = str(exc_info.value)
    assert "tag3, tag4" in error_message
    assert "gh label create" in error_message
    assert "https://github.com/test/repo/labels" in error_message


def test_validate_repository_labels_api_error() -> None:
    """Test _validate_repository_labels when GitHub API fails."""
    # Mock GitHub client with API error
    mock_client = Mock(spec=GitHubClient)
    mock_client.list_labels.side_effect = Exception("API error")
    mock_client.repo = "test/repo"

    required_tags = {"tag1"}

    # Should raise ClickException wrapping the original error
    with pytest.raises(Exception) as exc_info:
        _validate_repository_labels(mock_client, required_tags)

    error_message = str(exc_info.value)
    assert "Failed to validate repository labels" in error_message


def test_create_issues_with_tag_validation() -> None:
    """Test issue creation with tag validation enabled."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create a test JSON file with tags
        test_data = {
            "release": {"name": "Test Release"},
            "tasks": [
                {
                    "title": "Task 1",
                    "description": ["Description"],
                    "project": "Test",
                    "tags": ["bug", "feature"],
                    "category": "Testing",
                    "priority": 1,
                    "children": [
                        {
                            "title": "Subtask 1",
                            "description": ["Subdescription"],
                            "project": "Test",
                            "tags": ["enhancement"],
                            "category": "Testing",
                            "priority": 1,
                        }
                    ],
                }
            ],
        }

        Path("test_issues.json").write_text(json.dumps(test_data), encoding="utf-8")

        # Mock the GitHub client methods
        with patch("relprocotron.__main__.GitHubClient") as mock_github_client_class:
            mock_client = Mock()
            mock_github_client_class.return_value = mock_client

            # Mock labels that exist in the repository
            mock_client.list_labels.return_value = [
                {"name": "bug", "description": "Bug reports"},
                {"name": "feature", "description": "New features"},
                {"name": "enhancement", "description": "Enhancements"},
            ]

            # Mock successful issue creation
            mock_client.create_issue.return_value = {"number": 123, "url": "https://github.com/test/repo/issues/123"}
            mock_client.update_issue.return_value = {"number": 123}

            # Test issue creation with validation
            result = runner.invoke(
                main,
                [
                    "--create-issues",
                    "--input-file",
                    "test_issues.json",
                    "--github-repo",
                    "test/repo",
                    "--github-token",
                    "fake_token",
                    # Add minimal required options that won't be used in create-issues mode
                    "--release-name",
                    "dummy",
                    "--release-tag",
                    "dummy",
                    "--release-type",
                    "dev",
                    "--release-date",
                    "2025-01-01",
                    "--project-url",
                    "https://github.com/test/repo",
                    "--software-name",
                    "dummy",
                    "--software-version",
                    "1.0.0",
                    "--output-file",
                    "dummy.json",
                ],
            )

            # Should succeed
            assert result.exit_code == 0

            # Verify validation was called
            mock_client.list_labels.assert_called_once()

            # Verify issues were created
            assert mock_client.create_issue.call_count == 2  # 1 parent + 1 child


def test_create_issues_missing_tags_validation() -> None:
    """Test issue creation fails when required tags don't exist."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create a test JSON file with tags
        test_data = {
            "release": {"name": "Test Release"},
            "tasks": [
                {
                    "title": "Task 1",
                    "description": ["Description"],
                    "project": "Test",
                    "tags": ["missing-tag"],  # This tag doesn't exist
                    "category": "Testing",
                    "priority": 1,
                }
            ],
        }

        Path("test_issues.json").write_text(json.dumps(test_data), encoding="utf-8")

        # Mock the GitHub client methods
        with patch("relprocotron.__main__.GitHubClient") as mock_github_client_class:
            mock_client = Mock()
            mock_github_client_class.return_value = mock_client
            mock_client.repo = "test/repo"  # Set the repo attribute

            # Mock labels that exist in the repository (without the required tag)
            mock_client.list_labels.return_value = [
                {"name": "bug", "description": "Bug reports"},
                {"name": "feature", "description": "New features"},
            ]

            # Test issue creation with validation
            result = runner.invoke(
                main,
                [
                    "--create-issues",
                    "--input-file",
                    "test_issues.json",
                    "--github-repo",
                    "test/repo",
                    "--github-token",
                    "fake_token",
                    # Add minimal required options that won't be used in create-issues mode
                    "--release-name",
                    "dummy",
                    "--release-tag",
                    "dummy",
                    "--release-type",
                    "dev",
                    "--release-date",
                    "2025-01-01",
                    "--project-url",
                    "https://github.com/test/repo",
                    "--software-name",
                    "dummy",
                    "--software-version",
                    "1.0.0",
                    "--output-file",
                    "dummy.json",
                ],
            )

            # Should fail due to missing tags
            assert result.exit_code != 0

            # Verify error message contains expected content
            assert "missing-tag" in result.output
            assert "gh label create" in result.output
            assert "https://github.com/test/repo/labels" in result.output

            # Verify validation was called but no issues were created
            mock_client.list_labels.assert_called_once()
            mock_client.create_issue.assert_not_called()


def test_create_issues_dry_run_skips_validation() -> None:
    """Test that dry run mode skips tag validation."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create a test JSON file with tags
        test_data = {
            "release": {"name": "Test Release"},
            "tasks": [
                {
                    "title": "Task 1",
                    "description": ["Description"],
                    "project": "Test",
                    "tags": ["any-tag"],  # Tag doesn't need to exist in dry run
                    "category": "Testing",
                    "priority": 1,
                }
            ],
        }

        Path("test_issues.json").write_text(json.dumps(test_data), encoding="utf-8")

        # Test dry run mode
        result = runner.invoke(
            main,
            [
                "--create-issues",
                "--input-file",
                "test_issues.json",
                "--github-repo",
                "test/repo",
                "--github-token",
                "fake_token",
                "--dry-run",
                # Add minimal required options that won't be used in create-issues mode
                "--release-name",
                "dummy",
                "--release-tag",
                "dummy",
                "--release-type",
                "dev",
                "--release-date",
                "2025-01-01",
                "--project-url",
                "https://github.com/test/repo",
                "--software-name",
                "dummy",
                "--software-version",
                "1.0.0",
                "--output-file",
                "dummy.json",
            ],
        )

        # Should succeed in dry run mode
        assert result.exit_code == 0
        assert "any-tag" in result.output  # Should show the tag in output
