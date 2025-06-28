"""Tests for the main CLI module."""

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


def test_main_missing_required_args() -> None:
    """Test that the main command fails when required arguments are missing."""
    runner = CliRunner()
    result = runner.invoke(main, [])

    assert result.exit_code != 0
    assert "Missing option" in result.output


def test_main_with_valid_args() -> None:
    """Test that the main command runs successfully with valid arguments."""
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

    assert result.exit_code == 0
    assert "Release Process-O-Tron - Parameter Verification" in result.output
    assert "Release Name: Test Release" in result.output
    assert "Release Tag: v1.0.0" in result.output
    assert "Release Type: dev" in result.output


def test_main_with_dry_run() -> None:
    """Test that the main command respects the dry-run flag."""
    runner = CliRunner()
    result = runner.invoke(main, [
        "--release-name", "Test Release",
        "--release-tag", "v1.0.0",
        "--release-type", "LTS",
        "--release-date", "2025-01-20",
        "--project-url", "https://github.com/test/test",
        "--software-name", "Test Software",
        "--software-version", "1.0.0",
        "--dry-run"
    ])

    assert result.exit_code == 0
    assert "Dry Run: True" in result.output


def test_main_with_comments() -> None:
    """Test that the main command handles multiple comments."""
    runner = CliRunner()
    result = runner.invoke(main, [
        "--release-name", "Test Release",
        "--release-tag", "v1.0.0",
        "--release-type", "experimental",
        "--release-date", "2025-01-20",
        "--project-url", "https://github.com/test/test",
        "--software-name", "Test Software",
        "--software-version", "1.0.0",
        "--comment", "First comment",
        "--comment", "Second comment"
    ])

    assert result.exit_code == 0
    assert "Comments: ['First comment', 'Second comment']" in result.output


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
        "--software-version", "1.0.0"
    ])

    assert result.exit_code != 0
    assert "Invalid value for '--release-type'" in result.output
