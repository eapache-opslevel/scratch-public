#!/usr/bin/env python3
"""
Batch script to add static analysis workflows to multiple repositories.

This script processes multiple repositories in parallel or sequentially,
applying the static analysis workflow to each one and generating a consolidated
report of all operations.
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchWorkflowManager:
    """Manages batch operations for adding workflows to multiple repositories."""
    
    def __init__(self, repos: List[str], parallel: bool = False, max_workers: int = 4):
        """Initialize the batch manager.
        
        Args:
            repos: List of repository paths
            parallel: Whether to process repositories in parallel
            max_workers: Maximum number of parallel workers
        """
        self.repos = [Path(r).resolve() for r in repos]
        self.parallel = parallel
        self.max_workers = max_workers
        self.results = []
        
    def process_repository(self, repo_path: Path) -> Dict:
        """Process a single repository.
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            Dictionary with result information
        """
        logger.info(f"Processing repository: {repo_path}")
        
        result = {
            "repository": str(repo_path),
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": None
        }
        
        try:
            # Check if path exists and is a directory
            if not repo_path.exists():
                result["error"] = "Repository path does not exist"
                logger.error(f"{repo_path}: {result['error']}")
                return result
            
            if not repo_path.is_dir():
                result["error"] = "Repository path is not a directory"
                logger.error(f"{repo_path}: {result['error']}")
                return result
            
            # Check if it's a git repository
            git_dir = repo_path / ".git"
            if not git_dir.exists():
                result["error"] = "Not a git repository"
                logger.error(f"{repo_path}: {result['error']}")
                return result
            
            # Run the workflow script
            cmd = [
                sys.executable,
                str(Path(__file__).parent / "add-static-analysis-workflow.py"),
                str(repo_path)
            ]
            
            process_result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if process_result.returncode != 0:
                result["error"] = f"Script failed: {process_result.stderr}"
                logger.error(f"{repo_path}: {result['error']}")
                return result
            
            result["success"] = True
            logger.info(f"Successfully processed: {repo_path}")
            
        except subprocess.TimeoutExpired:
            result["error"] = "Script execution timed out"
            logger.error(f"{repo_path}: {result['error']}")
        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
            logger.error(f"{repo_path}: {result['error']}")
        
        return result
    
    def process_all(self) -> List[Dict]:
        """Process all repositories.
        
        Returns:
            List of result dictionaries
        """
        if self.parallel:
            return self._process_parallel()
        else:
            return self._process_sequential()
    
    def _process_sequential(self) -> List[Dict]:
        """Process repositories sequentially."""
        results = []
        total = len(self.repos)
        
        for idx, repo in enumerate(self.repos, 1):
            logger.info(f"Processing {idx}/{total}: {repo}")
            result = self.process_repository(repo)
            results.append(result)
        
        return results
    
    def _process_parallel(self) -> List[Dict]:
        """Process repositories in parallel."""
        results = []
        total = len(self.repos)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_repo = {
                executor.submit(self.process_repository, repo): repo
                for repo in self.repos
            }
            
            for idx, future in enumerate(as_completed(future_to_repo), 1):
                repo = future_to_repo[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"Completed {idx}/{total}: {repo}")
                except Exception as e:
                    logger.error(f"Error processing {repo}: {e}")
                    results.append({
                        "repository": str(repo),
                        "timestamp": datetime.now().isoformat(),
                        "success": False,
                        "error": str(e)
                    })
        
        return results
    
    def generate_summary_report(self, results: List[Dict]) -> Dict:
        """Generate a summary report of all operations.
        
        Args:
            results: List of result dictionaries
            
        Returns:
            Summary dictionary
        """
        total = len(results)
        successful = sum(1 for r in results if r["success"])
        failed = total - successful
        
        # Load individual tracking logs to get detailed actions
        actions = {"created": 0, "updated": 0, "skipped": 0}
        
        for result in results:
            if result["success"]:
                repo_path = Path(result["repository"])
                log_file = repo_path / "tracking-log.json"
                if log_file.exists():
                    try:
                        with open(log_file, 'r') as f:
                            logs = json.load(f)
                        if logs:
                            # Get the last entry for this repo
                            last_log = logs[-1]
                            action = last_log.get("action")
                            if action in actions:
                                actions[action] += 1
                    except Exception:
                        pass
        
        summary = {
            "total_repositories": total,
            "successful": successful,
            "failed": failed,
            "actions": actions,
            "timestamp": datetime.now().isoformat()
        }
        
        return summary
    
    def save_batch_report(self, results: List[Dict], output_file: str):
        """Save batch processing report to file.
        
        Args:
            results: List of result dictionaries
            output_file: Path to output file
        """
        summary = self.generate_summary_report(results)
        
        report = {
            "summary": summary,
            "results": results
        }
        
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Saved batch report to {output_path}")
    
    def print_summary(self, results: List[Dict]):
        """Print summary to console.
        
        Args:
            results: List of result dictionaries
        """
        summary = self.generate_summary_report(results)
        
        print("\n" + "=" * 80)
        print("BATCH PROCESSING SUMMARY")
        print("=" * 80)
        print(f"Total Repositories: {summary['total_repositories']}")
        print(f"Successful: {summary['successful']}")
        print(f"Failed: {summary['failed']}")
        print("\nActions Taken:")
        print(f"  - Created: {summary['actions']['created']}")
        print(f"  - Updated: {summary['actions']['updated']}")
        print(f"  - Skipped: {summary['actions']['skipped']}")
        print("=" * 80)
        
        if summary['failed'] > 0:
            print("\nFailed Repositories:")
            print("-" * 80)
            for result in results:
                if not result["success"]:
                    print(f"  - {result['repository']}: {result.get('error', 'Unknown error')}")
            print("=" * 80)


def read_repo_list(file_path: str) -> List[str]:
    """Read repository list from file.
    
    Args:
        file_path: Path to file containing repository paths (one per line)
        
    Returns:
        List of repository paths
    """
    repos = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                repos.append(line)
    return repos


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch add static analysis workflows to multiple repositories"
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--repos",
        nargs="+",
        help="List of repository paths"
    )
    group.add_argument(
        "--repo-file",
        help="File containing repository paths (one per line)"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Process repositories in parallel"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum number of parallel workers (default: 4)"
    )
    parser.add_argument(
        "--output",
        default="batch-report.json",
        help="Output file for batch report (default: batch-report.json)"
    )
    
    args = parser.parse_args()
    
    # Get repository list
    if args.repos:
        repos = args.repos
    else:
        repos = read_repo_list(args.repo_file)
    
    if not repos:
        logger.error("No repositories specified")
        return 1
    
    logger.info(f"Processing {len(repos)} repositories")
    
    # Process repositories
    manager = BatchWorkflowManager(repos, args.parallel, args.max_workers)
    results = manager.process_all()
    
    # Save report
    manager.save_batch_report(results, args.output)
    
    # Print summary
    manager.print_summary(results)
    
    # Return non-zero if any failed
    failed = sum(1 for r in results if not r["success"])
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
