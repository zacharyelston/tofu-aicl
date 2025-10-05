# WorkspaceData Data Model

## Schema

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class WorkspaceData:
    """
    Read-only snapshot of Replit workspace information
    """
    repl_id: str                     # Replit workspace ID
    title: str                       # Workspace title
    language: str                    # Primary programming language
    url: str                         # Workspace URL
    created_at: datetime             # Workspace creation time
    updated_at: datetime             # Last update time
    user_id: Optional[str]           # Owner user ID
    username: Optional[str]          # Owner username
    file_count: int                  # Number of files
    files: Optional[list[dict]]      # File metadata if requested
    metadata: dict                   # Additional workspace metadata

    @property
    def age_days(self) -> int:
        """Calculate workspace age in days"""
        return (datetime.utcnow() - self.created_at).days
```

## Validation Rules

- **repl_id**: Non-empty string
- **title**: Non-empty string
- **language**: Non-empty string
- **url**: Valid URL format
- **file_count**: Non-negative integer

## Example

```python
workspace = WorkspaceData(
    repl_id="repl-abc123",
    title="tofu-aicl",
    language="python",
    url="https://replit.com/@zacelston/tofu-aicl",
    created_at=datetime(2025, 9, 1, 0, 0, 0),
    updated_at=datetime(2025, 10, 5, 10, 0, 0),
    user_id="user-xyz789",
    username="zacelston",
    file_count=47,
    files=[
        {"name": "run.py", "type": "file"},
        {"name": "README.md", "type": "file"},
        {"name": "providers", "type": "directory"}
    ],
    metadata={
        "description": "Declarative AI Infrastructure",
        "stars": 5,
        "visibility": "public"
    }
)

# Usage
print(f"Workspace is {workspace.age_days} days old")
```

## Optional Fields

Fields that may be `None`:
- **user_id**: If include_user=false
- **username**: If include_user=false
- **files**: If include_files=false