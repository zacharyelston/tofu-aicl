"""
Test data preparation for RAG experiments.

Handles source code collection and snapshot creation.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from .git_utils import GitContext


class TestDataPreparer:
    """Prepares test data from source code for RAG experiments."""
    
    def __init__(self, data_dir: Path, repo_root: Path):
        self.data_dir = data_dir
        self.repo_root = repo_root
        self.git_context = GitContext()
    
    def prepare_test_data(self) -> Dict[str, Any]:
        """Prepare source code test data with git snapshot."""
        print("📁 Preparing test data from tofu-aicl source code...")
        
        # Create source snapshot directory
        snapshot_dir = self.data_dir / "source-snapshots" / self.git_context.sha
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Collect source files
        source_files = self._collect_source_files()
        
        test_data = {
            **self.git_context.to_dict(),
            "timestamp": datetime.utcnow().isoformat(),
            "source_files": source_files,
            "total_files": len(source_files),
            "snapshot_dir": str(snapshot_dir)
        }
        
        # Save test data manifest
        manifest_file = snapshot_dir / "manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        print(f"   ✅ Prepared {len(source_files)} source files")
        print(f"   📸 Snapshot saved to: {snapshot_dir}")
        
        return test_data
    
    def _collect_source_files(self) -> List[str]:
        """Collect relevant source files from the repository."""
        source_files = []
        
        # Collect documentation files
        docs_dir = self.repo_root / "docs"
        if docs_dir.exists():
            for doc_file in docs_dir.rglob("*.md"):
                if doc_file.is_file():
                    source_files.append(str(doc_file.relative_to(self.repo_root)))
        
        # Collect source code files
        src_dir = self.repo_root / "src"
        if src_dir.exists():
            for src_file in src_dir.rglob("*.py"):
                if src_file.is_file() and "__pycache__" not in str(src_file):
                    source_files.append(str(src_file.relative_to(self.repo_root)))
        
        # Collect API documentation
        api_docs_dir = self.repo_root / "APIDocs"
        if api_docs_dir.exists():
            for api_file in api_docs_dir.rglob("*.md"):
                if api_file.is_file():
                    source_files.append(str(api_file.relative_to(self.repo_root)))
        
        return source_files
    
    def get_context_limit(self, context_size: str) -> int:
        """Get file limit based on context size."""
        limits = {
            "tiny": 5,
            "small": 10,
            "medium": 25,
            "large": 50,
            "xlarge": 100,
            "xxlarge": 200
        }
        return limits.get(context_size, 25)
