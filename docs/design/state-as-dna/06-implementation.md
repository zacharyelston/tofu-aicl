# Implementation Guide

## State Manager Enhancement

### Current Implementation Issues

```python
# src/aicl/state/manager.py - Current problems:
class StateManager:
    def get_resource_by_name(self, name: str):
        for res in self.current_state.resources.values():
            if name in res.id:  # ❌ Substring matching!
                return res
```

Problems:
- No lineage tracking
- No git backend support
- Substring matching causes collisions
- No state lifecycle management

### Required Changes

#### 1. Enhanced State Structure

```python
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from pathlib import Path

@dataclass
class LineageEntry:
    timestamp: str
    action: str  # "provision", "execute", "destroy"
    resource_type: Optional[str] = None
    resource_name: Optional[str] = None
    provider: Optional[str] = None
    pipeline: Optional[str] = None
    step: Optional[str] = None
    input: Dict[str, Any] = field(default_factory=dict)
    result: Dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0
    cost_usd: Optional[float] = None

@dataclass
class Diagnostic:
    severity: str  # "info", "warning", "error"
    message: str
    timestamp: str

@dataclass
class Metadata:
    user: str
    host: str
    tofu_version: str
    config_file: str
    git_commit: Optional[str] = None

@dataclass
class State:
    version: str = "1.0"
    experiment_id: str = ""
    created_at: str = ""
    updated_at: str = ""
    metadata: Metadata = field(default_factory=Metadata)
    lineage: List[LineageEntry] = field(default_factory=list)
    current_state: Dict[str, Any] = field(default_factory=dict)
    diagnostics: List[Diagnostic] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        return {
            "version": self.version,
            "experiment_id": self.experiment_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": {
                "user": self.metadata.user,
                "host": self.metadata.host,
                "tofu_version": self.metadata.tofu_version,
                "config_file": self.metadata.config_file,
                "git_commit": self.metadata.git_commit
            },
            "lineage": [
                {k: v for k, v in entry.__dict__.items()}
                for entry in self.lineage
            ],
            "current_state": self.current_state,
            "diagnostics": [
                {k: v for k, v in diag.__dict__.items()}
                for diag in self.diagnostics
            ]
        }
```

#### 2. Backend Interface

```python
from abc import ABC, abstractmethod

class StateBackend(ABC):
    """Abstract base class for state backends"""
    
    @abstractmethod
    def load(self) -> State:
        """Load state from backend"""
        pass
    
    @abstractmethod
    def save(self, state: State) -> None:
        """Save state to backend"""
        pass
    
    @abstractmethod
    def lock(self) -> bool:
        """Acquire lock (if backend supports it)"""
        pass
    
    @abstractmethod
    def unlock(self) -> None:
        """Release lock"""
        pass

class LocalGitBackend(StateBackend):
    """Git-tracked local file backend (default)"""
    
    def __init__(self, state_dir: Path, experiment_id: str):
        self.state_dir = state_dir
        self.experiment_id = experiment_id
        self.state_file = state_dir / f"{experiment_id}.tfstate"
        self.state_dir.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> State:
        if not self.state_file.exists():
            return self._new_state()
        
        with open(self.state_file, 'r') as f:
            data = json.load(f)
            return self._dict_to_state(data)
    
    def save(self, state: State) -> None:
        state.updated_at = datetime.now().isoformat()
        
        with open(self.state_file, 'w') as f:
            json.dump(state.to_dict(), f, indent=2)
    
    def lock(self) -> bool:
        # Git backend doesn't need locking
        # Git itself handles conflicts
        return True
    
    def unlock(self) -> None:
        pass
    
    def _new_state(self) -> State:
        import socket
        import getpass
        
        return State(
            experiment_id=self.experiment_id,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            metadata=Metadata(
                user=getpass.getuser(),
                host=socket.gethostname(),
                tofu_version="0.1.0",  # Get from package
                config_file="",  # Set by engine
                git_commit=self._get_git_commit()
            ),
            current_state={
                "infrastructure": {},
                "outputs": {}
            }
        )
    
    def _get_git_commit(self) -> Optional[str]:
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=self.state_dir
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    def _dict_to_state(self, data: Dict) -> State:
        # Convert dict back to State object
        # ... implementation details ...
        pass

class S3Backend(StateBackend):
    """S3 + DynamoDB backend (optional)"""
    
    def __init__(self, bucket: str, key: str, region: str, 
                 dynamodb_table: str):
        self.bucket = bucket
        self.key = key
        self.region = region
        self.dynamodb_table = dynamodb_table
        # ... boto3 setup ...
    
    def load(self) -> State:
        # Load from S3
        pass
    
    def save(self, state: State) -> None:
        # Save to S3
        pass
    
    def lock(self) -> bool:
        # Acquire DynamoDB lock
        pass
    
    def unlock(self) -> None:
        # Release DynamoDB lock
        pass
```

#### 3. Enhanced State Manager

```python
class StateManager:
    def __init__(self, backend: StateBackend):
        self.backend = backend
        self.state = backend.load()
        self._current_action = None
    
    def record_provision(self, resource_type: str, resource_name: str,
                        provider: str, input_data: Dict, 
                        result: Dict, duration_ms: int):
        """Record a provisioning action"""
        entry = LineageEntry(
            timestamp=datetime.now().isoformat(),
            action="provision",
            resource_type=resource_type,
            resource_name=resource_name,
            provider=provider,
            input=input_data,
            result=result,
            duration_ms=duration_ms
        )
        self.state.lineage.append(entry)
        
        # Update current state
        resource_id = f"{resource_type}.{resource_name}"
        self.state.current_state["infrastructure"][resource_id] = {
            "id": result.get("id"),
            "provider": provider,
            "attributes": result,
            "dependencies": []
        }
        
        self.save()
    
    def record_execution(self, pipeline: str, step: str, provider: str,
                        input_data: Dict, result: Dict, 
                        duration_ms: int, cost_usd: Optional[float] = None):
        """Record a pipeline execution"""
        entry = LineageEntry(
            timestamp=datetime.now().isoformat(),
            action="execute",
            pipeline=pipeline,
            step=step,
            provider=provider,
            input=input_data,
            result=result,
            duration_ms=duration_ms,
            cost_usd=cost_usd
        )
        self.state.lineage.append(entry)
        
        # Update outputs
        if "outputs" not in self.state.current_state:
            self.state.current_state["outputs"] = {}
        
        # Aggregate metrics
        self._update_outputs(result, duration_ms, cost_usd)
        
        self.save()
    
    def record_destruction(self, resource_type: str, resource_name: str):
        """Record resource destruction"""
        entry = LineageEntry(
            timestamp=datetime.now().isoformat(),
            action="destroy",
            resource_type=resource_type,
            resource_name=resource_name
        )
        self.state.lineage.append(entry)
        
        # Remove from current state
        resource_id = f"{resource_type}.{resource_name}"
        if resource_id in self.state.current_state.get("infrastructure", {}):
            del self.state.current_state["infrastructure"][resource_id]
        
        self.save()
    
    def add_diagnostic(self, severity: str, message: str):
        """Add a diagnostic message"""
        diag = Diagnostic(
            severity=severity,
            message=message,
            timestamp=datetime.now().isoformat()
        )
        self.state.diagnostics.append(diag)
    
    def get_resource(self, resource_type: str, resource_name: str) -> Optional[Dict]:
        """Get resource by exact type and name"""
        resource_id = f"{resource_type}.{resource_name}"
        return self.state.current_state.get("infrastructure", {}).get(resource_id)
    
    def list_resources(self) -> List[str]:
        """List all resource IDs"""
        return list(self.state.current_state.get("infrastructure", {}).keys())
    
    def save(self):
        """Save state through backend"""
        self.backend.save(self.state)
    
    def _update_outputs(self, result: Dict, duration_ms: int, 
                       cost_usd: Optional[float]):
        outputs = self.state.current_state["outputs"]
        
        # Aggregate duration
        outputs["total_duration_ms"] = outputs.get("total_duration_ms", 0) + duration_ms
        
        # Aggregate cost
        if cost_usd:
            outputs["total_cost_usd"] = outputs.get("total_cost_usd", 0.0) + cost_usd
        
        # Add specific results
        for key, value in result.items():
            if isinstance(value, (int, float)):
                total_key = f"total_{key}"
                outputs[total_key] = outputs.get(total_key, 0) + value
```

## Integration with Engine

```python
# src/aicl/core/engine.py
class Engine:
    def __init__(self, config_file: str, experiment_id: str, 
                 backend_type: str = "local"):
        if backend_type == "local":
            backend = LocalGitBackend(
                state_dir=Path("terraform.tfstate.d"),
                experiment_id=experiment_id
            )
        elif backend_type == "s3":
            backend = S3Backend(...)  # Load from config
        else:
            raise ValueError(f"Unknown backend: {backend_type}")
        
        self.state_manager = StateManager(backend)
        # ... rest of init ...
    
    def apply(self):
        start_time = time.time()
        
        try:
            # Provision resources
            for resource in self.plan:
                resource_start = time.time()
                result = self._apply_resource(resource)
                duration_ms = int((time.time() - resource_start) * 1000)
                
                self.state_manager.record_provision(
                    resource_type=resource.type,
                    resource_name=resource.name,
                    provider=resource.provider,
                    input_data=resource.config,
                    result=result,
                    duration_ms=duration_ms
                )
        
        except Exception as e:
            self.state_manager.add_diagnostic("error", str(e))
            raise
```

## Testing Strategy

```python
# tests/test_state_manager.py
import pytest
from pathlib import Path
import json
import tempfile

def test_git_backend_creates_state():
    with tempfile.TemporaryDirectory() as tmpdir:
        backend = LocalGitBackend(
            state_dir=Path(tmpdir),
            experiment_id="test_001"
        )
        state = backend.load()
        assert state.experiment_id == "test_001"
        assert state.version == "1.0"

def test_lineage_tracking():
    with tempfile.TemporaryDirectory() as tmpdir:
        backend = LocalGitBackend(Path(tmpdir), "test")
        manager = StateManager(backend)
        
        manager.record_provision(
            resource_type="test_resource",
            resource_name="example",
            provider="test_provider",
            input_data={"config": "value"},
            result={"id": "test-123"},
            duration_ms=100
        )
        
        assert len(manager.state.lineage) == 1
        assert manager.state.lineage[0].action == "provision"
        
        # Verify file was written
        state_file = Path(tmpdir) / "test.tfstate"
        assert state_file.exists()
        
        # Verify JSON structure
        with open(state_file) as f:
            data = json.load(f)
            assert len(data["lineage"]) == 1
            assert data["lineage"][0]["resource_type"] == "test_resource"
```

## Migration Path

### Phase 1: Add Lineage Support
1. Implement new State dataclasses
2. Update StateManager with lineage tracking
3. **Keep existing functionality working**
4. Add tests

### Phase 2: Add Backend Abstraction
1. Create StateBackend interface
2. Implement LocalGitBackend
3. Update StateManager to use backend
4. **Maintain backwards compatibility**

### Phase 3: Integrate with Engine
1. Update Engine to use new StateManager
2. Record actions in lineage
3. Update outputs

### Phase 4: Optional S3 Backend
1. Implement S3Backend
2. Add configuration support
3. Documentation

## Files to Create/Modify

```
src/aicl/
├── state/
│   ├── __init__.py
│   ├── manager.py          # ✏️ Enhanced with lineage
│   ├── models.py           # 🆕 State dataclasses
│   └── backends/
│       ├── __init__.py     # 🆕
│       ├── base.py         # 🆕 StateBackend interface
│       ├── local.py        # 🆕 LocalGitBackend
│       └── s3.py           # 🆕 S3Backend (Phase 4)
├── core/
│   └── engine.py           # ✏️ Use new StateManager
└── ...

tests/
├── state/
│   ├── test_lineage.py     # 🆕
│   ├── test_local_backend.py  # 🆕
│   └── test_state_manager.py  # ✏️ Enhanced
└── ...
```

## Next Steps

1. Review this implementation plan
2. Create issues in Redmine for each phase
3. Implement Phase 1 (lineage support)
4. Validate with existing workflows
5. Continue to Phases 2-4
