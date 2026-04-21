#!/bin/bash
# Example usage scenarios for the static analysis workflow automation scripts

echo "=== Static Analysis Workflow Automation - Usage Examples ==="
echo

# Example 1: Dry run on current repository
echo "Example 1: Dry run on current repository"
echo "Command: python3 add-static-analysis-workflow.py --dry-run"
echo

# Example 2: Add workflow to current repository
echo "Example 2: Add workflow to current repository"
echo "Command: python3 add-static-analysis-workflow.py"
echo

# Example 3: Add workflow to specific repository
echo "Example 3: Add workflow to specific repository"
echo "Command: python3 add-static-analysis-workflow.py /path/to/repo"
echo

# Example 4: Batch process multiple repositories from command line
echo "Example 4: Batch process multiple repositories"
echo "Command: python3 batch-add-workflows.py --repos /path/to/repo1 /path/to/repo2"
echo

# Example 5: Batch process from file
echo "Example 5: Batch process from file"
echo "Command: python3 batch-add-workflows.py --repo-file repos.txt"
echo

# Example 6: Batch process in parallel
echo "Example 6: Batch process in parallel (faster for many repos)"
echo "Command: python3 batch-add-workflows.py --repo-file repos.txt --parallel --max-workers 8"
echo

# Example 7: Custom output file
echo "Example 7: Custom output file"
echo "Command: python3 batch-add-workflows.py --repo-file repos.txt --output my-report.json"
echo

# Example 8: Run tests
echo "Example 8: Run test suite"
echo "Command: python3 test_workflow_implementation.py"
echo
