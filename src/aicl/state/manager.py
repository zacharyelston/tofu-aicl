import json
import os
from pathlib import Path
from typing import Dict, Optional, Any
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime

@dataclass
class ResourceState:
    id: str
    type: str
    provider: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "unknown"

@dataclass
class StateFile:
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

class StateManager:
    def __init__(self, state_dir: str = "./terraform.tfstate.d"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.current_state: Optional[StateFile] = None

    def load(self, experiment_id: str) -> StateFile:
        """Load state from git-tracked file"""
        state_file = self.state_dir / f"{experiment_id}.tfstate"

        if state_file.exists():
            with open(state_file, 'r') as f:
                data = json.load(f)
                resources = {
                    k: ResourceState(**v) for k, v in data.get('resources', {}).items()
                }
                self.current_state = StateFile(
                    version=data.get('version', '1.0'),
                    experiment_id=data.get('experiment_id', experiment_id),
                    resources=resources,
                    outputs=data.get('outputs', {}),
                    metadata=data.get('metadata', {})
                )
        else:
            self.current_state = StateFile(experiment_id=experiment_id)

        return self.current_state

    def save(self) -> Optional[Path]:
        """Save state to git-tracked file"""
        if not self.current_state:
            return None

        state_file = self.state_dir / f"{self.current_state.experiment_id}.tfstate"
        self.current_state.metadata['last_modified'] = datetime.utcnow().isoformat()

        state_dict = asdict(self.current_state)

        temp_file = state_file.with_suffix('.tfstate.tmp')
        with open(temp_file, 'w') as f:
            json.dump(state_dict, f, indent=2)

        temp_file.replace(state_file)
        return state_file

    def add_resource(self, resource: ResourceState):
        if not self.current_state:
            raise RuntimeError("No state loaded. Call load() first.")
        self.current_state.resources[resource.id] = resource

    def get_resource(self, resource_id: str) -> Optional[ResourceState]:
        if not self.current_state:
            return None
        return self.current_state.resources.get(resource_id)

    def get_resource_by_name(self, resource_type: str, name: str) -> Optional[ResourceState]:
        """Get resource by exact type and name match."""
        if not self.current_state:
            return None

        # Look for exact match using type.name pattern
        for res in self.current_state.resources.values():
            if res.type == resource_type:
                # Extract resource name from ID (format: provider-name)
                res_name = res.id.split('-', 1)[1] if '-' in res.id else res.id
                if res_name == name:
                    return res
        return None

    def get_all_resources_as_dict(self) -> dict:
        if not self.current_state:
            return {}

        output = defaultdict(lambda: defaultdict(dict))
        for res in self.current_state.resources.values():
            # This is a simplification and assumes unique resource names
            res_name = res.id.split('-')[1] if '-' in res.id else res.id
            output[res.type][res_name] = {'attributes': res.attributes}
        return output

    def remove_resource(self, resource_id: str):
        if self.current_state and resource_id in self.current_state.resources:
            del self.current_state.resources[resource_id]

    def clear(self):
        if self.current_state:
            self.current_state.resources = {}
            self.current_state.outputs = {}