import json
import os
from pathlib import Path
from typing import Dict, Optional, Any, Union
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime
import time

# Import new models with lineage support
from .models import State, StateFile, ResourceState, LineageEntry, Diagnostic

# Legacy classes moved to models.py for backwards compatibility

class StateManager:
    """Enhanced StateManager with lineage tracking support.
    
    Supports both legacy StateFile format and new State format with lineage.
    Automatically migrates legacy state files to new format when loaded.
    """
    
    def __init__(self, state_dir: str = "./terraform.tfstate.d", enable_lineage: bool = True):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.current_state: Optional[Union[StateFile, State]] = None
        self.enable_lineage = enable_lineage
        self._action_start_time: Optional[float] = None

    def load(self, experiment_id: str) -> Union[StateFile, State]:
        """Load state from git-tracked file with automatic migration to new format."""
        state_file = self.state_dir / f"{experiment_id}.tfstate"

        if state_file.exists():
            with open(state_file, 'r') as f:
                data = json.load(f)
                
                # Check if this is a new format with lineage
                if 'lineage' in data and self.enable_lineage:
                    self.current_state = State.from_dict(data)
                else:
                    # Legacy format - create StateFile and optionally migrate
                    resources = {
                        k: ResourceState(**v) for k, v in data.get('resources', {}).items()
                    }
                    legacy_state = StateFile(
                        version=data.get('version', '1.0'),
                        experiment_id=data.get('experiment_id', experiment_id),
                        resources=resources,
                        outputs=data.get('outputs', {}),
                        metadata=data.get('metadata', {})
                    )
                    
                    if self.enable_lineage:
                        # Migrate to new format
                        self.current_state = legacy_state.to_state()
                        self.add_diagnostic(Diagnostic(
                            severity="info",
                            message=f"Migrated legacy state file to new format with lineage tracking",
                            source="StateManager.load"
                        ))
                    else:
                        self.current_state = legacy_state
        else:
            # New state file
            if self.enable_lineage:
                self.current_state = State(experiment_id=experiment_id)
            else:
                self.current_state = StateFile(experiment_id=experiment_id)

        return self.current_state

    def save(self) -> Optional[Path]:
        """Save state to git-tracked file with proper serialization."""
        if not self.current_state:
            return None

        state_file = self.state_dir / f"{self.current_state.experiment_id}.tfstate"
        
        # Update last modified timestamp
        if isinstance(self.current_state, State):
            self.current_state.metadata['last_modified'] = datetime.utcnow().isoformat()
            state_dict = self.current_state.to_dict()
        else:
            # Legacy StateFile
            self.current_state.metadata['last_modified'] = datetime.utcnow().isoformat()
            state_dict = asdict(self.current_state)

        # Atomic write
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
            if hasattr(self.current_state, 'outputs'):
                self.current_state.outputs = {}
    
    # New lineage tracking methods
    
    def _start_action_timer(self):
        """Start timing an action for duration tracking."""
        self._action_start_time = time.time()
    
    def _get_action_duration_ms(self) -> int:
        """Get duration of current action in milliseconds."""
        if self._action_start_time is None:
            return 0
        duration_ms = int((time.time() - self._action_start_time) * 1000)
        self._action_start_time = None
        return duration_ms
    
    def record_provision(self, 
                        resource_type: str,
                        resource_name: str, 
                        provider: str,
                        input_data: Dict[str, Any],
                        result: Dict[str, Any],
                        duration_ms: Optional[int] = None,
                        cost_usd: Optional[float] = None,
                        pipeline: Optional[str] = None,
                        step: Optional[str] = None) -> None:
        """Record a provision action in the lineage."""
        if not isinstance(self.current_state, State):
            return  # Skip lineage for legacy state
        
        if duration_ms is None:
            duration_ms = self._get_action_duration_ms()
        
        entry = LineageEntry(
            timestamp=datetime.utcnow().isoformat(),
            action="provision",
            resource_type=resource_type,
            resource_name=resource_name,
            provider=provider,
            pipeline=pipeline,
            step=step,
            input=input_data,
            result=result,
            duration_ms=duration_ms,
            cost_usd=cost_usd
        )
        
        self.current_state.add_lineage_entry(entry)
    
    def record_execution(self,
                        pipeline: str,
                        step: str,
                        input_data: Dict[str, Any],
                        result: Dict[str, Any],
                        duration_ms: Optional[int] = None,
                        cost_usd: Optional[float] = None,
                        resource_type: Optional[str] = None,
                        resource_name: Optional[str] = None,
                        provider: Optional[str] = None) -> None:
        """Record an execution action in the lineage."""
        if not isinstance(self.current_state, State):
            return  # Skip lineage for legacy state
        
        if duration_ms is None:
            duration_ms = self._get_action_duration_ms()
        
        entry = LineageEntry(
            timestamp=datetime.utcnow().isoformat(),
            action="execute",
            resource_type=resource_type,
            resource_name=resource_name,
            provider=provider,
            pipeline=pipeline,
            step=step,
            input=input_data,
            result=result,
            duration_ms=duration_ms,
            cost_usd=cost_usd
        )
        
        self.current_state.add_lineage_entry(entry)
    
    def record_destroy(self,
                      resource_type: str,
                      resource_name: str,
                      provider: str,
                      input_data: Dict[str, Any],
                      result: Dict[str, Any],
                      duration_ms: Optional[int] = None,
                      cost_usd: Optional[float] = None,
                      pipeline: Optional[str] = None,
                      step: Optional[str] = None) -> None:
        """Record a destroy action in the lineage."""
        if not isinstance(self.current_state, State):
            return  # Skip lineage for legacy state
        
        if duration_ms is None:
            duration_ms = self._get_action_duration_ms()
        
        entry = LineageEntry(
            timestamp=datetime.utcnow().isoformat(),
            action="destroy",
            resource_type=resource_type,
            resource_name=resource_name,
            provider=provider,
            pipeline=pipeline,
            step=step,
            input=input_data,
            result=result,
            duration_ms=duration_ms,
            cost_usd=cost_usd
        )
        
        self.current_state.add_lineage_entry(entry)
    
    def add_diagnostic(self, diagnostic: Diagnostic) -> None:
        """Add a diagnostic message to the state."""
        if isinstance(self.current_state, State):
            self.current_state.add_diagnostic(diagnostic)
    
    def start_action(self) -> None:
        """Start timing an action. Call before performing an operation."""
        self._start_action_timer()
    
    def get_lineage_summary(self) -> Dict[str, Any]:
        """Get a summary of the lineage for reporting."""
        if not isinstance(self.current_state, State):
            return {"lineage_enabled": False}
        
        actions_by_type = {}
        total_duration = 0
        total_cost = 0.0
        
        for entry in self.current_state.lineage:
            action = entry.action
            if action not in actions_by_type:
                actions_by_type[action] = 0
            actions_by_type[action] += 1
            total_duration += entry.duration_ms
            if entry.cost_usd:
                total_cost += entry.cost_usd
        
        return {
            "lineage_enabled": True,
            "total_actions": len(self.current_state.lineage),
            "actions_by_type": actions_by_type,
            "total_duration_ms": total_duration,
            "total_cost_usd": total_cost,
            "diagnostics_count": len(self.current_state.diagnostics)
        }