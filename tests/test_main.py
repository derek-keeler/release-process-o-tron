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


def test_main_missing_required_args() -> None:
    """Test that the main command fails when required arguments are missing."""
    runner = CliRunner()
    result = runner.invoke(main, [])

    assert result.exit_code != 0
    assert "Missing option" in result.output


def test_main_with_valid_args() -> None:
    """Test that the main command runs successfully with valid arguments."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, [
            "--release-name", "Test Release",
            "--release-tag", "v1.0.0",
            "--release-type", "dev",
            "--release-date", "2025-01-20",
            "--project-url", "https://github.com/test/test",
            "--software-name", "Test Software",
            "--software-version", "1.0.0",
            "--output-file", "test_output.json"
        ])

        assert result.exit_code == 0
        assert "Release Process-O-Tron - Parameter Verification" in result.output
        assert "Release Name: Test Release" in result.output
        assert "Release Tag: v1.0.0" in result.output
        assert "Release Type: dev" in result.output
        assert "Release activities written to: test_output.json" in result.output

        # Verify JSON file was created
        assert Path("test_output.json").exists()


def test_main_with_dry_run() -> None:
    """Test that the main command respects the dry-run flag."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, [
            "--release-name", "Test Release",
            "--release-tag", "v1.0.0",
            "--release-type", "LTS",
            "--release-date", "2025-01-20",
            "--project-url", "https://github.com/test/test",
            "--software-name", "Test Software",
            "--software-version", "1.0.0",
            "--dry-run",
            "--output-file", "dry_run_output.json"
        ])

        assert result.exit_code == 0
        assert "Dry Run: True" in result.output
        assert "Dry run mode - JSON generated but no files written" in result.output
        assert "Generated JSON content:" in result.output

        # Verify JSON file was NOT created in dry run mode
        assert not Path("dry_run_output.json").exists()

        # Verify that JSON content is displayed in the output
        assert '"name": "Test Release"' in result.output
        assert '"tag": "v1.0.0"' in result.output


def test_main_with_comments() -> None:
    """Test that the main command handles multiple comments."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, [
            "--release-name", "Test Release",
            "--release-tag", "v1.0.0",
            "--release-type", "experimental",
            "--release-date", "2025-01-20",
            "--project-url", "https://github.com/test/test",
            "--software-name", "Test Software",
            "--software-version", "1.0.0",
            "--comment", "First comment",
            "--comment", "Second comment",
            "--output-file", "comments_output.json"
        ])

        assert result.exit_code == 0
        assert "Comments: ['First comment', 'Second comment']" in result.output

        # Verify JSON file contains comments
        with Path("comments_output.json").open("r", encoding="utf-8") as f:
            data = json.load(f)
        assert "comments" in data["release"]
        assert data["release"]["comments"] == ["First comment", "Second comment"]


def test_invalid_release_type() -> None:
    """Test that invalid release type is rejected."""
    runner = CliRunner()
    result = runner.invoke(main, [
        "--release-name", "Test Release",
        "--release-tag", "v1.0.0",
        "--release-type", "invalid",
        "--release-date", "2025-01-20",
        "--project-url", "https://github.com/test/test",
        "--software-name", "Test Software",
        "--software-version", "1.0.0",
        "--output-file", "invalid_output.json"
    ])

    assert result.exit_code != 0
    assert "Invalid value for '--release-type'" in result.output


def test_json_structure_dev_release() -> None:
    """Test that generated JSON has correct structure for dev release."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, [
            "--release-name", "Dev Release",
            "--release-tag", "v1.0.0-dev",
            "--release-type", "dev",
            "--release-date", "2025-01-20",
            "--project-url", "https://github.com/test/test",
            "--software-name", "Test App",
            "--software-version", "1.0.0",
            "--output-file", "dev_release.json"
        ])

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
            assert isinstance(task["description"], list)
            assert isinstance(task["tags"], list)

            # Check children tasks if they exist
            if "children" in task:
                for child in task["children"]:
                    assert "title" in child
                    assert "description" in child
                    assert "project" in child
                    assert "tags" in child
                    assert "category" in child


def test_json_structure_lts_release() -> None:
    """Test that generated JSON includes publication tasks for LTS release."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, [
            "--release-name", "LTS Release",
            "--release-tag", "v2.0.0",
            "--release-type", "LTS",
            "--release-date", "2025-01-20",
            "--project-url", "https://github.com/test/test",
            "--software-name", "Test App",
            "--software-version", "2.0.0",
            "--output-file", "lts_release.json"
        ])

        assert result.exit_code == 0

        # Parse and validate JSON structure
        with Path("lts_release.json").open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Verify publication task exists for LTS release
        task_titles = [task["title"] for task in data["tasks"]]
        assert "Publication" in task_titles


def test_missing_output_file() -> None:
    """Test that missing output file argument is rejected."""
    runner = CliRunner()
    result = runner.invoke(main, [
        "--release-name", "Test Release",
        "--release-tag", "v1.0.0",
        "--release-type", "dev",
        "--release-date", "2025-01-20",
        "--project-url", "https://github.com/test/test",
        "--software-name", "Test Software",
        "--software-version", "1.0.0"
    ])

    assert result.exit_code != 0
    assert "Missing option '--output-file'" in result.output
