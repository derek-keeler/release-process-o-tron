#!/usr/bin/env python3
"""CLI entrypoint for Release Process-O-Tron."""

import json
import time
from pathlib import Path
from typing import Any

import click
import requests
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
    "--release-type", type=click.Choice(["LTS", "dev", "experimental", "early-access"], case_sensitive=True),
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
    help='Additional comments about the release (can be used multiple times)'
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
@click.option("-o", "--output-file", type=str, required=True, help="Path to output JSON file for release activities")
@click.option("-V", "--verbose", is_flag=True, default=False, help="Enable verbose (DEBUG) logging")
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
        release_name=release_name,  # type: ignore[arg-type]
        release_tag=release_tag,  # type: ignore[arg-type]
        release_type=release_type,  # type: ignore[arg-type]
        release_date=release_date,  # type: ignore[arg-type]
        project_url=project_url,  # type: ignore[arg-type]
        software_name=software_name,  # type: ignore[arg-type]
        software_version=software_version,  # type: ignore[arg-type]
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


class GitHubClient:
    """GitHub REST API client with retry functionality."""

    def __init__(self, token: str, repo: str) -> None:
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token
            repo: Repository in format 'owner/repo'
        """
        self.token = token
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "release-process-o-tron"
        })

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0
    ) -> dict[str, Any]:
        """Make HTTP request with retry logic and exponential backoff.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request payload
            max_retries: Maximum number of retry attempts
            base_delay: Base delay for exponential backoff

        Returns:
            Response data as dictionary

        Raises:
            requests.RequestException: If request fails after all retries
        """
        url = f"{self.base_url}{endpoint}"

        for attempt in range(max_retries + 1):
            try:
                if method.upper() == "GET":
                    response = self.session.get(url, timeout=30)
                elif method.upper() == "POST":
                    response = self.session.post(url, json=data, timeout=30)
                elif method.upper() == "PATCH":
                    response = self.session.patch(url, json=data, timeout=30)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                # Handle rate limiting with backoff
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", base_delay * (2 ** attempt)))
                    if attempt < max_retries:
                        msg = f"Rate limited, waiting {retry_after} seconds before retry {attempt + 1}/{max_retries}"
                        click.echo(msg)
                        time.sleep(retry_after)
                        continue

                # Handle successful responses
                if response.status_code in (200, 201):
                    response_data: dict[str, Any] = response.json()
                    return response_data

                # Handle client/server errors
                response.raise_for_status()

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)
                    msg = f"Request failed, retrying in {delay} seconds (attempt {attempt + 1}/{max_retries}): {e}"
                    click.echo(msg)
                    time.sleep(delay)
                    continue
                raise
            except requests.exceptions.RequestException:
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)
                    click.echo(f"Request failed, retrying in {delay} seconds (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    continue
                raise

        # If we get here, all retries failed
        raise requests.RequestException(f"Request to {url} failed after {max_retries} retries")

    def create_issue(self, title: str, body: str, labels: list[str] | None = None) -> dict[str, Any]:
        """Create a GitHub issue.

        Args:
            title: Issue title
            body: Issue body/description
            labels: List of label names

        Returns:
            Created issue data
        """
        data: dict[str, Any] = {
            "title": title,
            "body": body
        }
        if labels:
            data["labels"] = labels

        return self._make_request("POST", f"/repos/{self.repo}/issues", data)

    def get_issue(self, issue_number: int) -> dict[str, Any]:
        """Get issue details.

        Args:
            issue_number: Issue number

        Returns:
            Issue data
        """
        return self._make_request("GET", f"/repos/{self.repo}/issues/{issue_number}")

    def update_issue(self, issue_number: int, **kwargs: Any) -> dict[str, Any]:  # noqa: ANN401
        """Update an existing issue.

        Args:
            issue_number: Issue number
            **kwargs: Fields to update (title, body, labels, etc.)

        Returns:
            Updated issue data
        """
        return self._make_request("PATCH", f"/repos/{self.repo}/issues/{issue_number}", kwargs)


def _create_github_issues(input_file: str, github_repo: str, github_token: str, dry_run: bool) -> None:
    """Create GitHub issues from JSON file."""
    # Check if input file exists first
    input_path = Path(input_file)
    if not input_path.exists():
        raise click.ClickException(f"Input file not found: {input_file}")

    # Load JSON data
    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    click.echo(f"Creating GitHub issues for release: {data['release']['name']}")
    if dry_run:
        click.echo("DRY RUN: No actual issues will be created")

    # Initialize GitHub client only if not doing a dry run
    github_client = None
    if not dry_run:
        try:
            github_client = GitHubClient(github_token, github_repo)
        except Exception as e:
            raise click.ClickException(f"Failed to initialize GitHub client: {e}") from e

    # Sort tasks by priority for proper ordering
    tasks = sorted(data["tasks"], key=lambda x: x.get("priority", 999))

    # Track created issues for parent-child relationships
    created_issues: dict[str, dict[str, Any]] = {}
    total_created = 0

    # Create issues for all top-level tasks
    for task in tasks:
        parent_issue = _create_issue_from_task(github_client, task, None, dry_run)
        if parent_issue:
            created_issues[task["title"]] = parent_issue
            total_created += 1

        # Create child issues if they exist, sorted by priority
        if "children" in task:
            child_tasks = sorted(task["children"], key=lambda x: x.get("priority", 999))
            child_task_list = []

            for child_task in child_tasks:
                child_issue = _create_issue_from_task(github_client, child_task, parent_issue, dry_run)
                if child_issue:
                    created_issues[child_task["title"]] = child_issue
                    total_created += 1
                    child_task_list.append(f"- [ ] #{child_issue['number']} {child_task['title']}")

            # Update parent issue with task list of children (sub-issues)
            if parent_issue and child_task_list and not dry_run:
                try:
                    updated_body = parent_issue["body"] + "\n\n**Sub-tasks:**\n" + "\n".join(child_task_list)
                    if github_client:
                        github_client.update_issue(parent_issue["number"], body=updated_body)
                        click.echo(f"  Updated parent issue #{parent_issue['number']} with sub-task list")
                except Exception as e:  # noqa: BLE001 - GitHub API can raise various exceptions
                    click.echo(f"  Warning: Failed to update parent issue with sub-tasks: {e}", err=True)

    click.echo(f"Successfully created {total_created} issues")


def _create_issue_from_task(
    github_client: GitHubClient | None,
    task: dict[str, Any],
    parent_issue: dict[str, Any] | None,
    dry_run: bool
) -> dict[str, Any] | None:
    """Create a single GitHub issue from a task."""
    title = task["title"]

    # Build description from task description array
    description_lines = [f"**Category:** {task['category']}", ""]
    if task.get("description"):
        description_lines.extend(task["description"])

    # Add priority information
    if "priority" in task:
        description_lines.extend(["", f"**Priority:** {task['priority']}"])

    # Add parent reference if this is a child task
    if parent_issue:
        description_lines.extend(["", f"**Parent Issue:** #{parent_issue['number']}"])

    body = "\n".join(description_lines)

    # Use tags as labels
    labels = task.get("tags", [])

    click.echo(f"Creating issue: {title}")
    if dry_run:
        click.echo(f"  Body: {body[:100]}...")
        click.echo(f"  Labels: {labels}")
        if "priority" in task:
            click.echo(f"  Priority: {task['priority']}")
        return None

    try:
        if github_client is None:
            raise ValueError("GitHub client required for issue creation")
        issue = github_client.create_issue(title=title, body=body, labels=labels)
        click.echo(f"  Created issue #{issue['number']}")
        return issue
    except Exception as e:  # noqa: BLE001 - GitHub API can raise various exceptions
        click.echo(f"  Failed to create issue: {e}", err=True)
        return None


if __name__ == '__main__':
    main()
