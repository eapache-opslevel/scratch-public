# scratch-public

## Static Analysis Workflow Automation

This repository contains tools to automate the addition of standardized static analysis workflows to organization repositories.

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Add workflow to current repository
python3 add-static-analysis-workflow.py

# Or process multiple repositories
python3 batch-add-workflows.py --repo-file repos.txt
```

### Features

- ✅ Automatically detects repository default branch
- ✅ Creates standardized `.github/workflows/static-analysis.yaml` files
- ✅ Skips repositories that already have matching workflows
- ✅ Validates YAML syntax
- ✅ Tracks all operations in logs
- ✅ Supports batch processing of multiple repositories
- ✅ Parallel processing for large-scale operations

### Documentation

- [Quick Start Guide](QUICKSTART.md) - Get started in 5 minutes
- [Full Documentation](WORKFLOW_AUTOMATION.md) - Complete reference guide
- [Usage Examples](examples/usage-examples.sh) - Common usage scenarios

### Files

- `add-static-analysis-workflow.py` - Add workflow to a single repository
- `batch-add-workflows.py` - Process multiple repositories
- `test_workflow_implementation.py` - Test suite
- `requirements.txt` - Python dependencies

### Testing

Run the test suite to verify everything works:

```bash
python3 test_workflow_implementation.py
```

### Generated Workflow

The automation creates a workflow file that references the shared static analysis workflow:

```yaml
name: Static Analysis

on:
  push:
    branches:
      - main  # Automatically detected
  pull_request:
    branches:
      - main  # Automatically detected

jobs:
  static-analysis:
    uses: opslevel/.github/.github/workflows/static-analysis.yaml@main
```