"""
State as DNA: Enhanced state models with lineage tracking.

This module implements the core data structures for the State as DNA model,
where state files serve as comprehensive reports containing complete lineage
and current reality of AI infrastructure and pipelines.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


@dataclass
class LineageEntry:
    """
    Records a single action in the infrastructure lifecycle.
    
    Each entry represents one step in the "DNA" - the complete history
    of how the current state was achieved.
    """
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
    
    def __post_init__(self):
        """Ensure timestamp is set if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class Diagnostic:
    """
    Diagnostic message from state operations.
    
    Used to track warnings, errors, and informational messages
    during state lifecycle operations.
    """
    severity: str  # "info", "warning", "error"
    message: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    source: Optional[str] = None  # Which component generated this diagnostic


@dataclass
class ResourceState:
    """
    Current state of a single resource.
    
    Enhanced version of the original ResourceState with additional
    metadata for lineage tracking.
    """
    id: str
    type: str
    provider: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "unknown"
    created_at: Optional[str] = None
    last_modified: Optional[str] = None
    
    def __post_init__(self):
        """Set timestamps if not provided."""
        now = datetime.utcnow().isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.last_modified:
            self.last_modified = now


@dataclass
class State:
    """
    Complete state with lineage tracking - the "DNA" of the infrastructure.
    
    This is the enhanced version of StateFile that includes complete
    lineage tracking and diagnostic information.
    """
    version: str = "1.0"
    experiment_id: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Lineage: The complete "DNA" - history of all actions
    lineage: List[LineageEntry] = field(default_factory=list)
    
    # Current state: The "phenotype" - current reality
    resources: Dict[str, ResourceState] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    
    # Operational data
    diagnostics: List[Diagnostic] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize metadata if not provided."""
        if not self.metadata:
            self.metadata = {
                'created_at': self.created_at,
                'last_modified': self.created_at,
                'total_actions': 0,
                'total_cost_usd': 0.0
            }
    
    def add_lineage_entry(self, entry: LineageEntry):
        """Add a new lineage entry and update metadata."""
        self.lineage.append(entry)
        self.metadata['last_modified'] = datetime.utcnow().isoformat()
        self.metadata['total_actions'] = len(self.lineage)
        
        # Update total cost if provided
        if entry.cost_usd:
            current_cost = self.metadata.get('total_cost_usd', 0.0)
            self.metadata['total_cost_usd'] = current_cost + entry.cost_usd
    
    def add_diagnostic(self, diagnostic: Diagnostic):
        """Add a diagnostic message."""
        self.diagnostics.append(diagnostic)
    
    def get_lineage_by_action(self, action: str) -> List[LineageEntry]:
        """Get all lineage entries for a specific action type."""
        return [entry for entry in self.lineage if entry.action == action]
    
    def get_lineage_by_resource(self, resource_type: str, resource_name: str) -> List[LineageEntry]:
        """Get all lineage entries for a specific resource."""
        return [
            entry for entry in self.lineage 
            if entry.resource_type == resource_type and entry.resource_name == resource_name
        ]
    
    def get_total_duration_ms(self) -> int:
        """Get total duration of all actions."""
        return sum(entry.duration_ms for entry in self.lineage)
    
    def get_total_cost_usd(self) -> float:
        """Get total cost of all actions."""
        return sum(entry.cost_usd or 0.0 for entry in self.lineage)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'version': self.version,
            'experiment_id': self.experiment_id,
            'created_at': self.created_at,
            'lineage': [
                {
                    'timestamp': entry.timestamp,
                    'action': entry.action,
                    'resource_type': entry.resource_type,
                    'resource_name': entry.resource_name,
                    'provider': entry.provider,
                    'pipeline': entry.pipeline,
                    'step': entry.step,
                    'input': entry.input,
                    'result': entry.result,
                    'duration_ms': entry.duration_ms,
                    'cost_usd': entry.cost_usd
                }
                for entry in self.lineage
            ],
            'resources': {
                k: {
                    'id': v.id,
                    'type': v.type,
                    'provider': v.provider,
                    'attributes': v.attributes,
                    'metadata': v.metadata,
                    'status': v.status,
                    'created_at': v.created_at,
                    'last_modified': v.last_modified
                }
                for k, v in self.resources.items()
            },
            'outputs': self.outputs,
            'diagnostics': [
                {
                    'severity': d.severity,
                    'message': d.message,
                    'timestamp': d.timestamp,
                    'source': d.source
                }
                for d in self.diagnostics
            ],
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'State':
        """Create State from dictionary (JSON deserialization)."""
        # Parse lineage entries
        lineage = [
            LineageEntry(
                timestamp=entry['timestamp'],
                action=entry['action'],
                resource_type=entry.get('resource_type'),
                resource_name=entry.get('resource_name'),
                provider=entry.get('provider'),
                pipeline=entry.get('pipeline'),
                step=entry.get('step'),
                input=entry.get('input', {}),
                result=entry.get('result', {}),
                duration_ms=entry.get('duration_ms', 0),
                cost_usd=entry.get('cost_usd')
            )
            for entry in data.get('lineage', [])
        ]
        
        # Parse resources
        resources = {
            k: ResourceState(
                id=v['id'],
                type=v['type'],
                provider=v['provider'],
                attributes=v.get('attributes', {}),
                metadata=v.get('metadata', {}),
                status=v.get('status', 'unknown'),
                created_at=v.get('created_at'),
                last_modified=v.get('last_modified')
            )
            for k, v in data.get('resources', {}).items()
        }
        
        # Parse diagnostics
        diagnostics = [
            Diagnostic(
                severity=d['severity'],
                message=d['message'],
                timestamp=d.get('timestamp', datetime.utcnow().isoformat()),
                source=d.get('source')
            )
            for d in data.get('diagnostics', [])
        ]
        
        return cls(
            version=data.get('version', '1.0'),
            experiment_id=data.get('experiment_id', ''),
            created_at=data.get('created_at', datetime.utcnow().isoformat()),
            lineage=lineage,
            resources=resources,
            outputs=data.get('outputs', {}),
            diagnostics=diagnostics,
            metadata=data.get('metadata', {})
        )


# Backwards compatibility: Keep original StateFile for migration
@dataclass
class StateFile:
    """
    Original StateFile class for backwards compatibility.
    
    This will be deprecated in favor of the new State class
    but is kept during the migration period.
    """
    version: str = "1.0"
    experiment_id: str = ""
    resources: Dict[str, ResourceState] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not self.metadata:
            now = datetime.utcnow().isoformat()
            self.metadata = {
                'created_at': now,
                'last_modified': now
            }
    
    def to_state(self) -> State:
        """Convert legacy StateFile to new State format."""
        return State(
            version=self.version,
            experiment_id=self.experiment_id,
            created_at=self.metadata.get('created_at', datetime.utcnow().isoformat()),
            resources=self.resources,
            outputs=self.outputs,
            metadata=dict(self.metadata)  # Convert to Dict[str, Any]
        )
