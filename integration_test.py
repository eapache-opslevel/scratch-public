#!/usr/bin/env python3
"""
Comprehensive integration test for the static analysis workflow automation.

This test creates temporary repositories with different configurations and
verifies the automation handles them correctly.
"""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return result."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        shell=isinstance(cmd, str)
    )
    return result.returncode, result.stdout, result.stderr


def create_test_repo(path, branch_name="main"):
    """Create a test git repository."""
    path.mkdir(parents=True, exist_ok=True)
    
    # Initialize git repo
    run_command("git init", cwd=path)
    run_command("git config user.email 'test@example.com'", cwd=path)
    run_command("git config user.name 'Test User'", cwd=path)
    
    # Create initial commit
    readme = path / "README.md"
    readme.write_text("# Test Repository\n")
    run_command("git add README.md", cwd=path)
    run_command("git commit -m 'Initial commit'", cwd=path)
    
    # Get the actual initial branch name (could be master or main)
    returncode, stdout, stderr = run_command("git rev-parse --abbrev-ref HEAD", cwd=path)
    current_branch = stdout.strip()
    
    # Rename branch if needed
    if branch_name != current_branch:
        run_command(f"git branch -m {current_branch} {branch_name}", cwd=path)
    
    return path


def test_basic_workflow_creation():
    """Test creating workflow in a fresh repository."""
    print("\nTest: Basic workflow creation")
    print("-" * 80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir) / "test-repo"
        create_test_repo(repo_path)
        
        # Run the script
        script_path = Path(__file__).parent / "add-static-analysis-workflow.py"
        returncode, stdout, stderr = run_command(
            [sys.executable, str(script_path), str(repo_path)]
        )
        
        if returncode != 0:
            print(f"FAIL: Script failed: {stderr}")
            return False
        
        # Verify workflow file exists
        workflow_file = repo_path / ".github" / "workflows" / "static-analysis.yaml"
        if not workflow_file.exists():
            print("FAIL: Workflow file not created")
            return False
        
        # Verify content
        content = workflow_file.read_text()
        if "static-analysis:" not in content or "main" not in content:
            print("FAIL: Workflow content incorrect")
            return False
        
        print("PASS: Basic workflow creation works")
        return True


def test_custom_branch():
    """Test with a repository using a non-main branch."""
    print("\nTest: Custom branch detection")
    print("-" * 80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir) / "test-repo"
        create_test_repo(repo_path, branch_name="develop")
        
        # Run the script
        script_path = Path(__file__).parent / "add-static-analysis-workflow.py"
        returncode, stdout, stderr = run_command(
            [sys.executable, str(script_path), str(repo_path)]
        )
        
        if returncode != 0:
            print(f"FAIL: Script failed: {stderr}")
            return False
        
        # Verify workflow uses correct branch
        workflow_file = repo_path / ".github" / "workflows" / "static-analysis.yaml"
        content = workflow_file.read_text()
        
        if "develop" not in content:
            print(f"FAIL: Workflow doesn't use correct branch. Content:\n{content}")
            return False
        
        print("PASS: Custom branch detection works")
        return True


def test_idempotency():
    """Test that running twice doesn't cause issues."""
    print("\nTest: Idempotency")
    print("-" * 80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir) / "test-repo"
        create_test_repo(repo_path)
        
        script_path = Path(__file__).parent / "add-static-analysis-workflow.py"
        
        # Run once
        returncode1, stdout1, stderr1 = run_command(
            [sys.executable, str(script_path), str(repo_path)]
        )
        
        if returncode1 != 0:
            print(f"FAIL: First run failed: {stderr1}")
            return False
        
        # Get original content
        workflow_file = repo_path / ".github" / "workflows" / "static-analysis.yaml"
        original_content = workflow_file.read_text()
        
        # Run again
        returncode2, stdout2, stderr2 = run_command(
            [sys.executable, str(script_path), str(repo_path)]
        )
        
        if returncode2 != 0:
            print(f"FAIL: Second run failed: {stderr2}")
            return False
        
        # Verify content unchanged
        new_content = workflow_file.read_text()
        if original_content != new_content:
            print("FAIL: Content changed on second run")
            return False
        
        # Verify it was skipped
        if "skipped" not in stdout2.lower():
            print("FAIL: Second run didn't skip")
            return False
        
        print("PASS: Idempotency works")
        return True


def test_batch_processing():
    """Test batch processing multiple repositories."""
    print("\nTest: Batch processing")
    print("-" * 80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create multiple repos
        repos = []
        for i in range(3):
            repo_path = tmpdir / f"repo{i}"
            create_test_repo(repo_path)
            repos.append(repo_path)
        
        # Create repos file
        repos_file = tmpdir / "repos.txt"
        repos_file.write_text("\n".join(str(r) for r in repos))
        
        # Run batch script
        script_path = Path(__file__).parent / "batch-add-workflows.py"
        output_file = tmpdir / "batch-report.json"
        
        returncode, stdout, stderr = run_command([
            sys.executable,
            str(script_path),
            "--repo-file", str(repos_file),
            "--output", str(output_file)
        ])
        
        if returncode != 0:
            print(f"FAIL: Batch script failed: {stderr}")
            return False
        
        # Verify all repos have workflow
        for repo in repos:
            workflow_file = repo / ".github" / "workflows" / "static-analysis.yaml"
            if not workflow_file.exists():
                print(f"FAIL: Workflow not created in {repo}")
                return False
        
        # Verify report exists
        if not output_file.exists():
            print("FAIL: Batch report not created")
            return False
        
        print("PASS: Batch processing works")
        return True


def test_yaml_validation():
    """Test that YAML validation prevents invalid files."""
    print("\nTest: YAML validation")
    print("-" * 80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir) / "test-repo"
        create_test_repo(repo_path)
        
        # Run the script
        script_path = Path(__file__).parent / "add-static-analysis-workflow.py"
        returncode, stdout, stderr = run_command(
            [sys.executable, str(script_path), str(repo_path)]
        )
        
        if returncode != 0:
            print(f"FAIL: Script failed: {stderr}")
            return False
        
        # Verify YAML is valid
        workflow_file = repo_path / ".github" / "workflows" / "static-analysis.yaml"
        
        try:
            import yaml
            with open(workflow_file, 'r') as f:
                yaml.safe_load(f)
            print("PASS: YAML validation works")
            return True
        except yaml.YAMLError as e:
            print(f"FAIL: Generated YAML is invalid: {e}")
            return False


def main():
    """Run all integration tests."""
    print("=" * 80)
    print("Integration Tests for Static Analysis Workflow Automation")
    print("=" * 80)
    
    tests = [
        test_basic_workflow_creation,
        test_custom_branch,
        test_idempotency,
        test_batch_processing,
        test_yaml_validation,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"FAIL: Exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 80)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All integration tests passed!")
        return 0
    else:
        print("\n✗ Some integration tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
