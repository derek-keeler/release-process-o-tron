#!/usr/bin/env python3
"""CLI entrypoint for Release Process-O-Tron."""

import json
import logging
import tomllib
from pathlib import Path

import click
from jinja2 import Environment, FileSystemLoader

logging.basicConfig(level=logging.INFO)


def _get_value_from_pyproject(valkey: str) -> str:
    """Extract value from pyproject.toml in the project root using tomllib."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    try:
        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)
        # Try PEP 621-compliant location first
        if "project" in data and valkey in data["project"]:
            return str(data["project"][valkey])
    except Exception:
        logging.getLogger(__name__).error("Failed to read or parse pyproject.toml for version.")
        raise
    return "unknown"


@click.command()
@click.help_option("-h", "--help")
@click.version_option(
    _get_value_from_pyproject("version"),
    "-v",
    "--version",
    prog_name=_get_value_from_pyproject("name"),
    message="%(prog)s v%(version)s",
)  # Dynamic version from pyproject.toml
@click.option("-n", "--release-name", type=str, required=True, help="Name of the release")
@click.option("-t", "--release-tag", type=str, required=True, help="Git tag for the release")
@click.option(
    "-y",
    "--release-type",
    type=click.Choice(["LTS", "dev", "experimental", "early-access"], case_sensitive=True),
    required=True,
    help="Type of release (LTS, dev, experimental, early-access)",
)
@click.option("-d", "--release-date", type=str, required=True, help="Release date in YYYY-MM-DD format")
@click.option("-u", "--project-url", type=str, required=True, help="URL of the project repository")
@click.option("-r", "--dry-run", is_flag=True, default=False, help="Perform a dry run without making actual changes")
@click.option("-s", "--software-name", type=str, required=True, help="Name of the software being released")
@click.option("-S", "--software-version", type=str, required=True, help="Version of the software being released")
@click.option(
    "-c",
    "--comment",
    type=str,
    multiple=True,
    help="Additional comments about the release (can be used multiple times)",
)
@click.option("-o", "--output-file", type=str, required=True, help="Path to output JSON file for release activities")
@click.option("-V", "--verbose", is_flag=True, default=False, help="Enable verbose (DEBUG) logging")
def main(
    release_name: str,
    release_tag: str,
    release_type: str,
    release_date: str,
    project_url: str,
    dry_run: bool,
    software_name: str,
    software_version: str,
    comment: tuple[str, ...],
    output_file: str,
    verbose: bool,
) -> None:
    """Release Process-O-Tron CLI tool.

    Generate hierarchical work items for your upcoming release,
    and see the state of the release throughout its duration.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Verbose mode enabled: log level set to DEBUG.")

    # Convert tuple to list for consistency with type hint
    comment_list: list[str] = list(comment)

    # Log all received parameters for verification
    logging.info(
        f"{_get_value_from_pyproject('name')} v{_get_value_from_pyproject('version')} - Parameter Verification"
    )
    logging.info("=" * 50)
    logging.info(f"Release Name: {release_name}")
    logging.info(f"Release Tag: {release_tag}")
    logging.info(f"Release Type: {release_type}")
    logging.info(f"Release Date: {release_date}")
    logging.info(f"Project URL: {project_url}")
    logging.info(f"Dry Run: {dry_run}")
    logging.info(f"Software Name: {software_name}")
    logging.info(f"Software Version: {software_version}")
    logging.info(f"Comments: {comment_list}")
    logging.info(f"Output File: {output_file}")

    # Generate release activities JSON
    _generate_release_activities(
        release_name=release_name,
        release_tag=release_tag,
        release_type=release_type,
        release_date=release_date,
        project_url=project_url,
        software_name=software_name,
        software_version=software_version,
        comments=comment_list,
        output_file=output_file,
    )

    click.echo(f"\nRelease activities written to: {output_file}")


def _generate_release_activities(
    release_name: str,
    release_tag: str,
    release_type: str,
    release_date: str,
    project_url: str,
    software_name: str,
    software_version: str,
    comments: list[str],
    output_file: str,
) -> None:
    """Generate release activities JSON from template."""
    # Get template directory
    template_dir = Path(__file__).parent / "templates"

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(template_dir))  # noqa: S701 - JSON output, not HTML
    template = env.get_template("release_process_o_tron.j2.json")

    # Render template with provided data
    rendered_json = template.render(
        release_name=release_name,
        release_tag=release_tag,
        release_type=release_type,
        release_date=release_date,
        project_url=project_url,
        software_name=software_name,
        software_version=software_version,
        comments=comments,
    )

    # Parse to validate JSON format
    parsed_data = json.loads(rendered_json)

    # Write formatted JSON to output file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(parsed_data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
