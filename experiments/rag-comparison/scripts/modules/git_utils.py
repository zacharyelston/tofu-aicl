"""
Git utilities for RAG experiments.

Handles git context capture for reproducible experiments.
"""

import subprocess
from typing import Dict, Optional


class GitContext:
    """Captures and manages git context for experiments."""
    
    def __init__(self):
        self.sha = self._get_git_sha()
        self.branch = self._get_git_branch()
        self.has_uncommitted = self._has_uncommitted_changes()
    
    def _get_git_sha(self) -> str:
        """Get current git commit SHA (short form)."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"
    
    def _get_git_branch(self) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"
    
    def _has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, check=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False
    
    def create_experiment_id(self, provider: str, context_size: str, phase: int) -> str:
        """Create descriptive experiment ID with git context."""
        return f"phase{phase}_{provider}_{context_size}_{self.sha}"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert git context to dictionary."""
        return {
            "git_sha": self.sha,
            "git_branch": self.branch,
            "has_uncommitted_changes": self.has_uncommitted
        }
    
    def __str__(self) -> str:
        """String representation of git context."""
        status = " (uncommitted changes)" if self.has_uncommitted else ""
        return f"{self.branch}@{self.sha}{status}"
