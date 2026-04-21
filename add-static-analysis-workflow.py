#!/usr/bin/env python3
"""
Script to add standardized static analysis workflow to organization repositories.

This script:
- Creates .github/workflows/ directory if it doesn't exist
- Adds static-analysis.yaml workflow file using a shared workflow template
- Detects each repository's default branch name
- Configures push.branches trigger to reference the detected default branch
- Compares existing static-analysis.yaml files against the standard template
- Skips repositories where the file already exists and matches the template
- Validates YAML syntax before committing changes
- Documents which repositories were updated vs. skipped in tracking logs
"""

import os
import sys
import subprocess
import yaml
from pathlib import Path
from typing import Optional, Tuple
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Shared workflow template
STATIC_ANALYSIS_TEMPLATE = """name: Static Analysis

on:
  push:
    branches:
      - {default_branch}
  pull_request:
    branches:
      - {default_branch}

jobs:
  static-analysis:
    uses: opslevel/.github/.github/workflows/static-analysis.yaml@main
"""


class StaticAnalysisWorkflowManager:
    """Manages the addition of static analysis workflows to repositories."""
    
    def __init__(self, repo_path: str):
        """Initialize the workflow manager.
        
        Args:
            repo_path: Path to the repository root
        """
        self.repo_path = Path(repo_path).resolve()
        self.workflows_dir = self.repo_path / ".github" / "workflows"
        self.workflow_file = self.workflows_dir / "static-analysis.yaml"
        self.tracking_log = []
        
    def detect_default_branch(self) -> Optional[str]:
        """Detect the repository's default branch name.
        
        Returns:
            The default branch name (e.g., 'main', 'master', 'develop') or None if detection fails
        """
        try:
            # Try to get the default branch from git
            result = subprocess.run(
                ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                # Output format: "refs/remotes/origin/main"
                branch = result.stdout.strip().split('/')[-1]
                logger.info(f"Detected default branch: {branch}")
                return branch
            
            # Fallback: check current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                branch = result.stdout.strip()
                logger.info(f"Using current branch as default: {branch}")
                return branch
                
            logger.warning("Could not detect default branch")
            return None
            
        except Exception as e:
            logger.error(f"Error detecting default branch: {e}")
            return None
    
    def validate_yaml(self, content: str) -> bool:
        """Validate YAML syntax.
        
        Args:
            content: YAML content to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            yaml.safe_load(content)
            return True
        except yaml.YAMLError as e:
            logger.error(f"YAML validation error: {e}")
            return False
    
    def generate_workflow_content(self, default_branch: str) -> str:
        """Generate the workflow file content.
        
        Args:
            default_branch: The default branch name to use in the workflow
            
        Returns:
            The formatted workflow content
        """
        return STATIC_ANALYSIS_TEMPLATE.format(default_branch=default_branch)
    
    def normalize_yaml(self, content: str) -> str:
        """Normalize YAML content for comparison.
        
        This handles minor formatting differences that don't affect functionality.
        
        Args:
            content: YAML content to normalize
            
        Returns:
            Normalized content
        """
        try:
            # Parse and re-dump to normalize formatting
            data = yaml.safe_load(content)
            return yaml.dump(data, default_flow_style=False, sort_keys=False)
        except yaml.YAMLError:
            # If parsing fails, return original
            return content
    
    def files_match(self, existing_content: str, new_content: str) -> bool:
        """Check if existing file matches the new content.
        
        Args:
            existing_content: Content of existing file
            new_content: Content of new file
            
        Returns:
            True if files match, False otherwise
        """
        # Normalize both for comparison
        normalized_existing = self.normalize_yaml(existing_content)
        normalized_new = self.normalize_yaml(new_content)
        
        return normalized_existing == normalized_new
    
    def create_workflows_directory(self) -> bool:
        """Create .github/workflows/ directory if it doesn't exist.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.workflows_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created/verified workflows directory: {self.workflows_dir}")
            return True
        except Exception as e:
            logger.error(f"Error creating workflows directory: {e}")
            return False
    
    def should_update_workflow(self, workflow_content: str) -> Tuple[bool, str]:
        """Determine if the workflow file should be updated.
        
        Args:
            workflow_content: The new workflow content to write
            
        Returns:
            Tuple of (should_update, reason)
        """
        if not self.workflow_file.exists():
            return True, "File does not exist"
        
        try:
            existing_content = self.workflow_file.read_text()
            
            if self.files_match(existing_content, workflow_content):
                return False, "File already exists and matches template"
            
            return True, "File exists but content differs"
            
        except Exception as e:
            logger.error(f"Error reading existing workflow file: {e}")
            return True, f"Error reading existing file: {e}"
    
    def write_workflow_file(self, content: str) -> bool:
        """Write the workflow file.
        
        Args:
            content: Content to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.workflow_file.write_text(content)
            logger.info(f"Written workflow file: {self.workflow_file}")
            return True
        except Exception as e:
            logger.error(f"Error writing workflow file: {e}")
            return False
    
    def add_workflow(self) -> dict:
        """Add or update the static analysis workflow.
        
        Returns:
            Dictionary with result information
        """
        result = {
            "repository": str(self.repo_path),
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "action": None,
            "reason": None,
            "default_branch": None
        }
        
        # Detect default branch
        default_branch = self.detect_default_branch()
        if not default_branch:
            result["reason"] = "Could not detect default branch"
            logger.error(result["reason"])
            return result
        
        result["default_branch"] = default_branch
        
        # Generate workflow content
        workflow_content = self.generate_workflow_content(default_branch)
        
        # Validate YAML
        if not self.validate_yaml(workflow_content):
            result["reason"] = "Generated workflow has invalid YAML syntax"
            logger.error(result["reason"])
            return result
        
        # Check if update is needed
        should_update, reason = self.should_update_workflow(workflow_content)
        result["reason"] = reason
        
        if not should_update:
            result["success"] = True
            result["action"] = "skipped"
            logger.info(f"Skipping: {reason}")
            return result
        
        # Create directory if needed
        if not self.create_workflows_directory():
            result["reason"] = "Failed to create workflows directory"
            logger.error(result["reason"])
            return result
        
        # Write workflow file
        if not self.write_workflow_file(workflow_content):
            result["reason"] = "Failed to write workflow file"
            logger.error(result["reason"])
            return result
        
        result["success"] = True
        result["action"] = "updated" if self.workflow_file.exists() else "created"
        logger.info(f"Successfully {result['action']} workflow file")
        
        return result
    
    def save_tracking_log(self, result: dict, log_file: Optional[str] = None):
        """Save tracking log to file.
        
        Args:
            result: Result dictionary from add_workflow
            log_file: Path to log file (default: tracking-log.json in repo)
        """
        if log_file is None:
            log_file = self.repo_path / "tracking-log.json"
        else:
            log_file = Path(log_file)
        
        try:
            # Load existing log if it exists
            logs = []
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            
            # Append new result
            logs.append(result)
            
            # Save updated log
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
            
            logger.info(f"Saved tracking log to {log_file}")
            
        except Exception as e:
            logger.error(f"Error saving tracking log: {e}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Add standardized static analysis workflow to repositories"
    )
    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Path to repository (default: current directory)"
    )
    parser.add_argument(
        "--log-file",
        help="Path to tracking log file (default: tracking-log.json in repo)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = StaticAnalysisWorkflowManager(args.repo_path)
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
        default_branch = manager.detect_default_branch()
        if default_branch:
            workflow_content = manager.generate_workflow_content(default_branch)
            print("\nGenerated workflow content:")
            print("-" * 80)
            print(workflow_content)
            print("-" * 80)
            should_update, reason = manager.should_update_workflow(workflow_content)
            print(f"\nAction needed: {'Yes' if should_update else 'No'}")
            print(f"Reason: {reason}")
        else:
            print("ERROR: Could not detect default branch")
        return 0
    
    # Add workflow
    result = manager.add_workflow()
    
    # Save tracking log
    manager.save_tracking_log(result, args.log_file)
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Repository: {result['repository']}")
    print(f"Default Branch: {result['default_branch']}")
    print(f"Action: {result['action']}")
    print(f"Success: {result['success']}")
    print(f"Reason: {result['reason']}")
    print("=" * 80)
    
    return 0 if result['success'] else 1


if __name__ == "__main__":
    sys.exit(main())
