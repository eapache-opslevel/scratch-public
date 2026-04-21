# Static Analysis Workflow Automation

This repository contains tools to automate the addition of standardized static analysis workflows to organization repositories.

## Overview

The automation ensures all organization repositories have a standardized static analysis workflow by adding `.github/workflows/static-analysis.yaml` files that use a shared workflow template. The implementation is repository-agnostic and intelligently handles existing files.

## Features

- ✅ Creates `.github/workflows/` directory if it doesn't exist
- ✅ Adds `static-analysis.yaml` workflow file using shared workflow template
- ✅ Detects each repository's default branch name (e.g., `main`, `master`, `develop`)
- ✅ Configures `push.branches` trigger to reference the detected default branch
- ✅ Compares existing `static-analysis.yaml` files against the standard template
- ✅ Skips repositories where the file already exists and matches the template
- ✅ Handles repositories with custom branch naming conventions
- ✅ Ensures workflow file permissions and formatting are consistent
- ✅ Validates YAML syntax before committing changes
- ✅ Documents which repositories were updated vs. skipped in tracking logs
- ✅ Supports batch processing of multiple repositories
- ✅ Parallel processing support for large-scale operations

## Files

### Core Scripts

- **`add-static-analysis-workflow.py`**: Main script to add workflow to a single repository
- **`batch-add-workflows.py`**: Batch script to process multiple repositories
- **`test_workflow_implementation.py`**: Test suite to verify implementation

### Configuration

- **`requirements.txt`**: Python dependencies

### Generated Files

- **`.github/workflows/static-analysis.yaml`**: The workflow file (created in target repos)
- **`tracking-log.json`**: JSON log of operations (created in target repos)
- **`batch-report.json`**: Consolidated report for batch operations

## Installation

### Prerequisites

- Python 3.7 or higher
- Git
- pip (Python package manager)

### Setup

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

### Single Repository

#### Basic Usage

```bash
# Add workflow to current repository
python3 add-static-analysis-workflow.py

# Add workflow to specific repository
python3 add-static-analysis-workflow.py /path/to/repo
```

#### Dry Run

Preview what would be done without making changes:

```bash
python3 add-static-analysis-workflow.py --dry-run
```

#### Custom Log File

Specify a custom location for the tracking log:

```bash
python3 add-static-analysis-workflow.py --log-file /path/to/custom-log.json
```

### Multiple Repositories

#### From Command Line

```bash
# Process multiple repositories
python3 batch-add-workflows.py --repos /path/to/repo1 /path/to/repo2 /path/to/repo3

# Process in parallel for faster execution
python3 batch-add-workflows.py --repos /path/to/repo1 /path/to/repo2 --parallel
```

#### From File

Create a file with repository paths (one per line):

```text
# repos.txt
/path/to/repo1
/path/to/repo2
/path/to/repo3
```

Then process:

```bash
python3 batch-add-workflows.py --repo-file repos.txt
```

#### Parallel Processing

For large numbers of repositories, use parallel processing:

```bash
python3 batch-add-workflows.py --repo-file repos.txt --parallel --max-workers 8
```

#### Custom Output

Specify custom output file for batch report:

```bash
python3 batch-add-workflows.py --repo-file repos.txt --output my-report.json
```

## Workflow Template

The generated workflow file follows this standard template:

```yaml
name: Static Analysis

on:
  push:
    branches:
      - main  # Automatically detected for each repo
  pull_request:
    branches:
      - main  # Automatically detected for each repo

jobs:
  static-analysis:
    uses: opslevel/.github/.github/workflows/static-analysis.yaml@main
```

The `main` branch reference is automatically replaced with the detected default branch for each repository.

## Behavior

### File Existence Check

The script checks if `.github/workflows/static-analysis.yaml` already exists:

- **Does not exist**: Creates the file with the standard template
- **Exists and matches**: Skips the repository (no changes needed)
- **Exists but differs**: Updates the file to match the standard template

### Branch Detection

The script automatically detects the default branch using:

1. Git symbolic ref for `origin/HEAD`
2. Current branch as fallback
3. Common defaults (main, master, develop) as last resort

### YAML Validation

All generated workflow files are validated for:

- Valid YAML syntax
- Proper structure
- Required fields

### Tracking Logs

Each operation is logged with:

- Timestamp
- Repository path
- Success/failure status
- Action taken (created, updated, skipped)
- Default branch detected
- Reason for action

## Testing

Run the test suite to verify the implementation:

```bash
python3 test_workflow_implementation.py
```

Expected output:

```
================================================================================
Testing Static Analysis Workflow Implementation
================================================================================

Test: Script exists
--------------------------------------------------------------------------------
PASS: Script exists

Test: Script is executable
--------------------------------------------------------------------------------
PASS: Script is executable

Test: Dry run mode
--------------------------------------------------------------------------------
PASS: Dry run works

Test: Actual execution
--------------------------------------------------------------------------------
PASS: Actual run created workflow file

Test: Idempotency
--------------------------------------------------------------------------------
PASS: Idempotency check passed

Test: Tracking log
--------------------------------------------------------------------------------
PASS: Tracking log created with 2 entries

================================================================================
TEST SUMMARY
================================================================================
Passed: 6/6

✓ All tests passed!
```

## Output Examples

### Single Repository Output

```
2024-01-01 12:00:00 - INFO - Detected default branch: main
2024-01-01 12:00:00 - INFO - Created/verified workflows directory: /path/to/repo/.github/workflows
2024-01-01 12:00:00 - INFO - Written workflow file: /path/to/repo/.github/workflows/static-analysis.yaml
2024-01-01 12:00:00 - INFO - Successfully created workflow file
2024-01-01 12:00:00 - INFO - Saved tracking log to /path/to/repo/tracking-log.json

================================================================================
SUMMARY
================================================================================
Repository: /path/to/repo
Default Branch: main
Action: created
Success: True
Reason: File does not exist
================================================================================
```

### Batch Processing Output

```
================================================================================
BATCH PROCESSING SUMMARY
================================================================================
Total Repositories: 10
Successful: 9
Failed: 1

Actions Taken:
  - Created: 5
  - Updated: 2
  - Skipped: 2

================================================================================

Failed Repositories:
--------------------------------------------------------------------------------
  - /path/to/broken-repo: Not a git repository
================================================================================
```

## Tracking Log Format

The `tracking-log.json` file contains entries like:

```json
[
  {
    "repository": "/path/to/repo",
    "timestamp": "2024-01-01T12:00:00.000000",
    "success": true,
    "action": "created",
    "reason": "File does not exist",
    "default_branch": "main"
  }
]
```

## Batch Report Format

The `batch-report.json` file contains:

```json
{
  "summary": {
    "total_repositories": 10,
    "successful": 9,
    "failed": 1,
    "actions": {
      "created": 5,
      "updated": 2,
      "skipped": 2
    },
    "timestamp": "2024-01-01T12:00:00.000000"
  },
  "results": [
    {
      "repository": "/path/to/repo1",
      "timestamp": "2024-01-01T12:00:00.000000",
      "success": true,
      "error": null
    }
  ]
}
```

## Error Handling

The scripts handle various error conditions:

- **Repository not found**: Logs error and continues with next repo (batch mode)
- **Not a git repository**: Logs error and skips
- **Permission errors**: Logs error and skips
- **YAML validation fails**: Prevents file creation and logs error
- **Branch detection fails**: Logs error and skips repository

## Best Practices

1. **Test First**: Always run with `--dry-run` on a test repository first
2. **Review Logs**: Check tracking logs to verify operations
3. **Backup**: Consider backing up repositories before batch operations
4. **Parallel Carefully**: Use parallel processing only after testing sequential mode
5. **Monitor Progress**: Check batch reports for any failed repositories

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'yaml'"

**Solution**: Install dependencies with `pip install -r requirements.txt`

### Issue: "Could not detect default branch"

**Solution**: Ensure the repository has a valid git configuration and remote tracking branch

### Issue: "Permission denied"

**Solution**: Ensure you have write permissions to the repository directory

### Issue: "YAML validation error"

**Solution**: This indicates a bug in the template. Report the issue with the error message.

## Integration with CI/CD

The scripts can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Update Static Analysis Workflows

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  update-workflows:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run batch update
        run: python3 batch-add-workflows.py --repo-file repos.txt
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: batch-report
          path: batch-report.json
```

## Contributing

When contributing improvements:

1. Update test suite for new features
2. Ensure all tests pass
3. Update documentation
4. Follow existing code style
5. Add tracking for new operations

## License

[Add appropriate license information]

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review tracking logs for detailed error information
3. Open an issue with relevant log excerpts
