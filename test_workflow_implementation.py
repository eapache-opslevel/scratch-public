#!/usr/bin/env python3
"""
Test script to verify the static analysis workflow implementation.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        shell=True
    )
    return result.returncode, result.stdout, result.stderr

def test_script_exists():
    """Test that the script exists."""
    script_path = Path("/scratch-public/add-static-analysis-workflow.py")
    if not script_path.exists():
        print("FAIL: Script does not exist")
        return False
    print("PASS: Script exists")
    return True

def test_script_is_executable():
    """Test that the script can be executed."""
    returncode, stdout, stderr = run_command(
        "python3 /scratch-public/add-static-analysis-workflow.py --help"
    )
    if returncode != 0:
        print(f"FAIL: Script help failed: {stderr}")
        return False
    print("PASS: Script is executable")
    return True

def test_dry_run():
    """Test dry run mode."""
    returncode, stdout, stderr = run_command(
        "python3 /scratch-public/add-static-analysis-workflow.py /scratch-public --dry-run"
    )
    if returncode != 0:
        print(f"FAIL: Dry run failed: {stderr}")
        return False
    if "Generated workflow content:" not in stdout:
        print(f"FAIL: Dry run did not show workflow content")
        return False
    print("PASS: Dry run works")
    return True

def test_actual_run():
    """Test actual execution."""
    returncode, stdout, stderr = run_command(
        "python3 /scratch-public/add-static-analysis-workflow.py /scratch-public"
    )
    if returncode != 0:
        print(f"FAIL: Actual run failed: {stderr}")
        return False
    
    # Check if workflow file was created
    workflow_file = Path("/scratch-public/.github/workflows/static-analysis.yaml")
    if not workflow_file.exists():
        print("FAIL: Workflow file was not created")
        return False
    
    # Check content
    content = workflow_file.read_text()
    if "static-analysis:" not in content:
        print("FAIL: Workflow file does not contain expected content")
        return False
    
    print("PASS: Actual run created workflow file")
    return True

def test_idempotency():
    """Test that running again doesn't change anything."""
    returncode, stdout, stderr = run_command(
        "python3 /scratch-public/add-static-analysis-workflow.py /scratch-public"
    )
    if returncode != 0:
        print(f"FAIL: Second run failed: {stderr}")
        return False
    
    if "skipped" not in stdout.lower():
        print(f"FAIL: Second run did not skip: {stdout}")
        return False
    
    print("PASS: Idempotency check passed")
    return True

def test_tracking_log():
    """Test that tracking log is created."""
    log_file = Path("/scratch-public/tracking-log.json")
    if not log_file.exists():
        print("FAIL: Tracking log was not created")
        return False
    
    import json
    try:
        with open(log_file, 'r') as f:
            logs = json.load(f)
        if not isinstance(logs, list):
            print("FAIL: Tracking log is not a list")
            return False
        if len(logs) == 0:
            print("FAIL: Tracking log is empty")
            return False
        print(f"PASS: Tracking log created with {len(logs)} entries")
        return True
    except Exception as e:
        print(f"FAIL: Error reading tracking log: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 80)
    print("Testing Static Analysis Workflow Implementation")
    print("=" * 80)
    
    tests = [
        ("Script exists", test_script_exists),
        ("Script is executable", test_script_is_executable),
        ("Dry run mode", test_dry_run),
        ("Actual execution", test_actual_run),
        ("Idempotency", test_idempotency),
        ("Tracking log", test_tracking_log),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nTest: {test_name}")
        print("-" * 80)
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"FAIL: Exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
