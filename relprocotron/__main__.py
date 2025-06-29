#!/usr/bin/env python3
"""CLI entrypoint for Release Process-O-Tron."""

import json
from pathlib import Path
from typing import Any

import click
from jinja2 import Environment, FileSystemLoader

try:
    from github import Github
    from github.Issue import Issue
    from github.Repository import Repository
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    Repository = Any  # type: ignore[misc,assignment]


@click.command()
@click.option(
    '--release-name',
    type=str,
    help='Name of the release'
)
@click.option(
    '--release-tag',
    type=str,
    help='Git tag for the release'
)
@click.option(
    '--release-type',
    type=click.Choice(['LTS', 'dev', 'experimental', 'early-access'], case_sensitive=True),
    help='Type of release (LTS, dev, experimental, early-access)'
)
@click.option(
    '--release-date',
    type=str,
    help='Release date in YYYY-MM-DD format'
)
@click.option(
    '--project-url',
    type=str,
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
    help='Name of the software being released'
)
@click.option(
    '--software-version',
    type=str,
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
    help='Path to output JSON file for release activities'
)
@click.option(
    '--create-issues',
    type=bool,
    is_flag=True,
    default=False,
    help='Create GitHub issues from existing JSON file'
)
@click.option(
    '--input-file',
    type=str,
    help='Path to input JSON file for issue creation (required when --create-issues is used)'
)
@click.option(
    '--github-repo',
    type=str,
    help='GitHub repository in format owner/repo (required when --create-issues is used)'
)
@click.option(
    '--github-token',
    type=str,
    help='GitHub personal access token (required when --create-issues is used)'
)
def main(
    release_name: str | None,
    release_tag: str | None,
    release_type: str | None,
    release_date: str | None,
    project_url: str | None,
    dry_run: bool,
    software_name: str | None,
    software_version: str | None,
    comment: tuple[str, ...],
    output_file: str | None,
    create_issues: bool,
    input_file: str | None,
    github_repo: str | None,
    github_token: str | None
) -> None:
    """Release Process-O-Tron CLI tool.

    Generate hierarchical work items for your upcoming release,
    and see the state of the release throughout its duration.
    """
    # Handle GitHub issue creation mode
    if create_issues:
        if not input_file or not github_repo or not github_token:
            click.echo("Error: --create-issues requires --input-file, --github-repo, and --github-token", err=True)
            raise click.ClickException("Missing required options for issue creation")

        _create_github_issues(input_file, github_repo, github_token, dry_run)
        return

    # For JSON generation mode, check required parameters
    required_params = [
        release_name, release_tag, release_type, release_date,
        project_url, software_name, software_version, output_file
    ]
    if not all(required_params):
        click.echo("Error: Missing required options for JSON generation", err=True)
        required_options = [
            "--release-name", "--release-tag", "--release-type", "--release-date",
            "--project-url", "--software-name", "--software-version", "--output-file"
        ]
        click.echo(f"Required: {', '.join(required_options)}")
        raise click.ClickException("Missing required options for JSON generation")

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
        release_name=release_name,  # type: ignore[arg-type]
        release_tag=release_tag,  # type: ignore[arg-type]
        release_type=release_type,  # type: ignore[arg-type]
        release_date=release_date,  # type: ignore[arg-type]
        project_url=project_url,  # type: ignore[arg-type]
        software_name=software_name,  # type: ignore[arg-type]
        software_version=software_version,  # type: ignore[arg-type]
        comments=comment_list,
        output_file=output_file  # type: ignore[arg-type]
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


def _create_github_issues(input_file: str, github_repo: str, github_token: str, dry_run: bool) -> None:
    """Create GitHub issues from JSON file."""
    if not GITHUB_AVAILABLE:
        raise click.ClickException(
            "PyGithub is not installed. Install with: pip install 'release-process-o-tron[github]'"
        )

    # Load JSON data
    input_path = Path(input_file)
    if not input_path.exists():
        raise click.ClickException(f"Input file not found: {input_file}")

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    click.echo(f"Creating GitHub issues for release: {data['release']['name']}")
    if dry_run:
        click.echo("DRY RUN: No actual issues will be created")

    # Initialize GitHub client only if not doing a dry run
    repo = None
    if not dry_run:
        try:
            github = Github(github_token)
            repo = github.get_repo(github_repo)
        except Exception as e:
            raise click.ClickException(f"Failed to connect to GitHub repository: {e}") from e

    # Track created issues for parent-child relationships
    created_issues: dict[str, Issue] = {}

    # Create issues for all top-level tasks
    for task in data["tasks"]:
        parent_issue = _create_issue_from_task(repo, task, None, dry_run)
        if parent_issue:
            created_issues[task["title"]] = parent_issue

        # Create child issues if they exist
        if "children" in task:
            for child_task in task["children"]:
                child_issue = _create_issue_from_task(repo, child_task, parent_issue, dry_run)
                if child_issue:
                    created_issues[child_task["title"]] = child_issue

    click.echo(f"Successfully created {len(created_issues)} issues")


def _create_issue_from_task(
    repo: Repository | None, task: dict[str, Any], parent_issue: Issue | None, dry_run: bool
) -> Issue | None:
    """Create a single GitHub issue from a task."""
    title = task["title"]

    # Build description from task description array
    description_lines = [f"**Category:** {task['category']}", ""]
    if task.get("description"):
        description_lines.extend(task["description"])

    # Add parent reference if this is a child task
    if parent_issue:
        description_lines.extend(["", f"**Parent Issue:** #{parent_issue.number}"])

    body = "\n".join(description_lines)

    # Use tags as labels
    labels = task.get("tags", [])

    click.echo(f"Creating issue: {title}")
    if dry_run:
        click.echo(f"  Body: {body[:100]}...")
        click.echo(f"  Labels: {labels}")
        return None

    try:
        if repo is None:
            raise ValueError("Repository connection required for issue creation")
        issue = repo.create_issue(title=title, body=body, labels=labels)
        click.echo(f"  Created issue #{issue.number}")
        return issue
    except Exception as e:  # noqa: BLE001 - GitHub API can raise various exceptions
        click.echo(f"  Failed to create issue: {e}", err=True)
        return None


if __name__ == '__main__':
    main()
