#!/usr/bin/env python3
"""CLI entrypoint for Release Process-O-Tron."""

import json
from pathlib import Path

import click
from jinja2 import Environment, FileSystemLoader


@click.command()
@click.option(
    '--release-name',
    type=str,
    required=True,
    help='Name of the release'
)
@click.option(
    '--release-tag',
    type=str,
    required=True,
    help='Git tag for the release'
)
@click.option(
    '--release-type',
    type=click.Choice(['LTS', 'dev', 'experimental', 'early-access'], case_sensitive=True),
    required=True,
    help='Type of release (LTS, dev, experimental, early-access)'
)
@click.option(
    '--release-date',
    type=str,
    required=True,
    help='Release date in YYYY-MM-DD format'
)
@click.option(
    '--project-url',
    type=str,
    required=True,
    help='URL of the project repository'
)
@click.option(
    '--dry-run',
    type=bool,
    is_flag=True,
    default=False,
    help='Perform a dry run without making actual changes'
)
@click.option(
    '--software-name',
    type=str,
    required=True,
    help='Name of the software being released'
)
@click.option(
    '--software-version',
    type=str,
    required=True,
    help='Version of the software being released'
)
@click.option(
    '--comment',
    type=str,
    multiple=True,
    help='Additional comments about the release (can be used multiple times)'
)
@click.option(
    '--output-file',
    type=str,
    required=True,
    help='Path to output JSON file for release activities'
)
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
    output_file: str
) -> None:
    """Release Process-O-Tron CLI tool.

    Generate hierarchical work items for your upcoming release,
    and see the state of the release throughout its duration.
    """
    # Convert tuple to list for consistency with type hint
    comment_list: list[str] = list(comment)

    # Echo all received parameters for verification
    click.echo("Release Process-O-Tron - Parameter Verification")
    click.echo("=" * 50)
    click.echo(f"Release Name: {release_name}")
    click.echo(f"Release Tag: {release_tag}")
    click.echo(f"Release Type: {release_type}")
    click.echo(f"Release Date: {release_date}")
    click.echo(f"Project URL: {project_url}")
    click.echo(f"Dry Run: {dry_run}")
    click.echo(f"Software Name: {software_name}")
    click.echo(f"Software Version: {software_version}")
    click.echo(f"Comments: {comment_list}")
    click.echo(f"Output File: {output_file}")

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
        output_file=output_file
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
        comments=comments
    )

    # Parse to validate JSON format
    parsed_data = json.loads(rendered_json)

    # Write formatted JSON to output file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(parsed_data, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
