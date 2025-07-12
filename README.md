# release-process-o-tron
Generate hierarchical work items for your upcoming release, and see the state of the release throughout it's duration.

## GitHub Workflow

This repository includes a GitHub workflow that can be manually triggered to create GitHub issues for an upcoming release. The workflow is located at `.github/workflows/create-release-issues.yml`.

### Usage

1. Go to the **Actions** tab in your GitHub repository
2. Select **Create Release Issues** from the workflow list
3. Click **Run workflow**
4. Fill in the required parameters:
   - **Release Name**: Name of the release
   - **Release Tag**: Git tag for the release
   - **Release Type**: Type of release (LTS, dev, experimental, early-access)
   - **Release Date**: Release date in YYYY-MM-DD format
   - **Project URL**: URL of the project repository
   - **Software Name**: Name of the software being released
   - **Software Version**: Version of the software being released
   - **Comments**: Additional comments about the release (optional)
   - **GitHub Repository**: GitHub repository in format owner/repo
   - **Dry Run**: Perform a dry run without creating actual issues (optional)

The workflow will generate a release activities JSON file and create GitHub issues based on the predefined templates.
