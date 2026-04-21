# Static Analysis Workflow Automation - File Index

## Core Scripts

### Main Automation Script
- **`add-static-analysis-workflow.py`** - Primary script to add/update static analysis workflow in a single repository
  - Detects default branch automatically
  - Validates YAML syntax
  - Compares with existing files
  - Creates tracking logs
  - Usage: `python3 add-static-analysis-workflow.py [repo_path]`

### Batch Processing Script
- **`batch-add-workflows.py`** - Process multiple repositories at once
  - Sequential or parallel execution
  - Consolidated reporting
  - Handles failures gracefully
  - Usage: `python3 batch-add-workflows.py --repos repo1 repo2` or `--repo-file repos.txt`

## Testing

### Unit Tests
- **`test_workflow_implementation.py`** - Core functionality tests
  - Tests script execution
  - Verifies file creation
  - Checks idempotency
  - Validates tracking logs
  - Run: `python3 test_workflow_implementation.py`

### Integration Tests
- **`integration_test.py`** - End-to-end testing
  - Creates temporary test repositories
  - Tests branch detection
  - Verifies batch processing
  - Tests YAML validation
  - Run: `python3 integration_test.py`

## Documentation

### Getting Started
- **`README.md`** - Repository overview with quick start
- **`QUICKSTART.md`** - 5-minute quick start guide
- **`WORKFLOW_AUTOMATION.md`** - Complete reference documentation

### Configuration
- **`requirements.txt`** - Python dependencies (PyYAML)
- **`.gitignore`** - Git ignore patterns

### Examples
- **`examples/repos-example.txt`** - Example repository list format
- **`examples/usage-examples.sh`** - Common usage scenarios

## Generated Files

### Workflow File (in target repositories)
- **`.github/workflows/static-analysis.yaml`** - The standardized workflow
  - Uses shared OpsLevel template
  - Configured with detected default branch
  - Triggers on push and pull_request

### Logs (in target repositories)
- **`tracking-log.json`** - Operation history
  - Timestamps
  - Actions taken (created/updated/skipped)
  - Branch information
  - Success/failure status

### Reports (from batch operations)
- **`batch-report.json`** - Consolidated batch processing report
  - Summary statistics
  - Individual repository results
  - Error details

## Workflow Template

The automation creates this standardized workflow:

```yaml
name: Static Analysis

on:
  push:
    branches:
      - [detected-branch]
  pull_request:
    branches:
      - [detected-branch]

jobs:
  static-analysis:
    uses: opslevel/.github/.github/workflows/static-analysis.yaml@main
```

## Dependencies

- Python 3.7+
- PyYAML 6.0+
- Git

## Quick Reference

### Single Repository
```bash
python3 add-static-analysis-workflow.py /path/to/repo
```

### Dry Run
```bash
python3 add-static-analysis-workflow.py --dry-run
```

### Multiple Repositories
```bash
python3 batch-add-workflows.py --repo-file repos.txt
```

### Parallel Processing
```bash
python3 batch-add-workflows.py --repo-file repos.txt --parallel --max-workers 8
```

### Run Tests
```bash
python3 test_workflow_implementation.py
python3 integration_test.py
```

## Support

For detailed usage instructions, see:
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [WORKFLOW_AUTOMATION.md](WORKFLOW_AUTOMATION.md) - Full documentation
