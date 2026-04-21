"""
Shared utilities for test scripts.
"""

import subprocess
from typing import Tuple


def run_command(cmd, cwd=None) -> Tuple[int, str, str]:
    """Run a command and return the result.
    
    Args:
        cmd: Command to run (string or list)
        cwd: Working directory for the command
        
    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        shell=isinstance(cmd, str)
    )
    return result.returncode, result.stdout, result.stderr
