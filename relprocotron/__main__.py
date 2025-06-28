#!/usr/bin/env python3
"""CLI entrypoint for Release Process-O-Tron."""

from typing import List
import click


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
def main(
    release_name: str,
    release_tag: str,
    release_type: str,
    release_date: str,
    project_url: str,
    dry_run: bool,
    software_name: str,
    software_version: str,
    comment: tuple[str, ...]
) -> None:
    """Release Process-O-Tron CLI tool.
    
    Generate hierarchical work items for your upcoming release,
    and see the state of the release throughout its duration.
    """
    # Convert tuple to list for consistency with type hint
    comment_list: List[str] = list(comment)
    
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


if __name__ == '__main__':
    main()