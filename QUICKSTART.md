# Quick Start Guide

Get started with the Static Analysis Workflow Automation in 5 minutes.

## Prerequisites

```bash
# Ensure Python 3.7+ is installed
python3 --version

# Ensure Git is installed
git --version
```

## Installation

```bash
# 1. Clone or navigate to this repository
cd /path/to/this/repo

# 2. Install dependencies
pip install -r requirements.txt
```

## Quick Usage

### Option 1: Single Repository

```bash
# Add workflow to the current repository
python3 add-static-analysis-workflow.py

# Or specify a repository path
python3 add-static-analysis-workflow.py /path/to/target/repo
```

### Option 2: Multiple Repositories

```bash
# Create a text file with repository paths (one per line)
cat > repos.txt << EOF
/path/to/repo1
/path/to/repo2
/path/to/repo3
EOF

# Process all repositories
python3 batch-add-workflows.py --repo-file repos.txt
```

## Verify Results

### Check Individual Repository

```bash
# View the generated workflow file
cat /path/to/repo/.github/workflows/static-analysis.yaml

# View the tracking log
cat /path/to/repo/tracking-log.json
```

### Check Batch Results

```bash
# View the batch report
cat batch-report.json

# Or use jq for pretty output
jq . batch-report.json
```

## Common Scenarios

### Dry Run First (Recommended)

Before making changes, see what would happen:

```bash
python3 add-static-analysis-workflow.py --dry-run
```

### Process Many Repositories Quickly

Use parallel processing for better performance:

```bash
python3 batch-add-workflows.py --repo-file repos.txt --parallel --max-workers 8
```

### Re-run Safely

The scripts are idempotent - running them multiple times won't cause issues:

```bash
# Running again on the same repo will skip if nothing changed
python3 add-static-analysis-workflow.py /path/to/repo
# Output: "Action: skipped - File already exists and matches template"
```

## Workflow File Example

The generated `.github/workflows/static-analysis.yaml` will look like:

```yaml
name: Static Analysis

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  static-analysis:
    uses: opslevel/.github/.github/workflows/static-analysis.yaml@main
```

The branch name (`main`) is automatically detected for each repository.

## What Gets Created

After running the script on a repository, you'll have:

```
repository/
├── .github/
│   └── workflows/
│       └── static-analysis.yaml  ← The workflow file
└── tracking-log.json             ← Operation log
```

## Next Steps

- Read [WORKFLOW_AUTOMATION.md](WORKFLOW_AUTOMATION.md) for detailed documentation
- Run the test suite: `python3 test_workflow_implementation.py`
- Check examples in the `examples/` directory

## Troubleshooting

### "No module named 'yaml'"

```bash
pip install PyYAML
```

### "Could not detect default branch"

The repository might not have a remote tracking branch set up. Check:

```bash
cd /path/to/repo
git remote -v
git branch -a
```

### Need Help?

Run with `-h` or `--help` for command options:

```bash
python3 add-static-analysis-workflow.py --help
python3 batch-add-workflows.py --help
```
