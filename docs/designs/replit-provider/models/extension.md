# ReplitExtension Data Model

## Schema

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional
import re

@dataclass
class ReplitExtension:
    """
    Represents a Replit extension instance managed by the provider
    """
    id: str                          # Unique identifier (ext-{uuid})
    name: str                        # Extension name (1-255 chars)
    version: str                     # Semver version
    handshake_status: HandshakeStatus  # Enum: PENDING, COMPLETE, FAILED
    dispose_function: Optional[Callable]  # JavaScript cleanup function reference
    created_at: datetime             # Timestamp of initialization
    auto_start: bool                 # Whether extension auto-starts
    timeout: int                     # Handshake timeout in milliseconds

    def __post_init__(self):
        """Validate extension data after initialization"""
        if not 1 <= len(self.name) <= 255:
            raise ValueError(f"Extension name must be 1-255 chars, got {len(self.name)}")
        if not re.match(r'^\d+\.\d+\.\d+$', self.version):
            raise ValueError(f"Invalid semver version: {self.version}")
        if not 1000 <= self.timeout <= 60000:
            raise ValueError(f"Timeout must be 1000-60000ms, got {self.timeout}")
```

## Validation Rules

- **id**: Non-empty string, format: `ext-[a-f0-9-]{36}`
- **name**: Required, 1-255 chars, alphanumeric + spaces/hyphens/underscores
- **version**: Required, semver pattern `^\d+\.\d+\.\d+$`
- **handshake_status**: One of: PENDING, COMPLETE, FAILED
- **timeout**: Integer 1000-60000 (1-60 seconds)

## Relationships

- **HAS_MANY**: AuthSession (one extension can support multiple auth sessions)

## State Transitions

```
PENDING → COMPLETE (handshake successful)
PENDING → FAILED (handshake timeout or error)
```

## Example

```python
extension = ReplitExtension(
    id="ext-550e8400-e29b-41d4-a716-446655440000",
    name="AI Workflow Manager",
    version="1.0.0",
    handshake_status=HandshakeStatus.COMPLETE,
    dispose_function=lambda: cleanup(),
    created_at=datetime(2025, 10, 5, 10, 30, 0),
    auto_start=True,
    timeout=5000
)
```