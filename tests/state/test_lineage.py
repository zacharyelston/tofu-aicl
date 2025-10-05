"""
Tests for State as DNA lineage tracking functionality.

This module tests the enhanced state management with complete lineage tracking,
ensuring that all actions are properly recorded in the "DNA" of the infrastructure.
"""

import json
import tempfile
import pytest
from pathlib import Path
from datetime import datetime

from src.aicl.state.manager import StateManager
from src.aicl.state.models import State, LineageEntry, Diagnostic, ResourceState


class TestLineageTracking:
    """Test lineage tracking functionality."""
    
    def test_new_state_has_empty_lineage(self):
        """Test that new state starts with empty lineage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(state_dir=tmpdir, enable_lineage=True)
            state = manager.load("test_experiment")
            
            assert isinstance(state, State)
            assert len(state.lineage) == 0
            assert state.experiment_id == "test_experiment"
            assert state.version == "1.0"
    
    def test_record_provision_action(self):
        """Test recording a provision action in lineage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(state_dir=tmpdir, enable_lineage=True)
            state = manager.load("test_experiment")
            
            # Record a provision action
            manager.record_provision(
                resource_type="pinecone_index",
                resource_name="embeddings",
                provider="pinecone",
                input_data={"dimension": 1536, "metric": "cosine"},
                result={"id": "embeddings-abc123", "status": "ready"},
                duration_ms=1500,
                cost_usd=0.05,
                pipeline="ai_setup",
                step="create_index"
            )
            
            # Verify lineage entry was created
            assert len(state.lineage) == 1
            entry = state.lineage[0]
            
            assert entry.action == "provision"
            assert entry.resource_type == "pinecone_index"
            assert entry.resource_name == "embeddings"
            assert entry.provider == "pinecone"
            assert entry.pipeline == "ai_setup"
            assert entry.step == "create_index"
            assert entry.input == {"dimension": 1536, "metric": "cosine"}
            assert entry.result == {"id": "embeddings-abc123", "status": "ready"}
            assert entry.duration_ms == 1500
            assert entry.cost_usd == 0.05
            assert entry.timestamp is not None
    
    def test_record_execution_action(self):
        """Test recording an execution action in lineage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(state_dir=tmpdir, enable_lineage=True)
            state = manager.load("test_experiment")
            
            # Record an execution action
            manager.record_execution(
                pipeline="data_processing",
                step="embed_documents",
                input_data={"documents": ["doc1.txt", "doc2.txt"]},
                result={"embeddings_created": 2, "total_tokens": 1024},
                duration_ms=3000,
                cost_usd=0.02,
                resource_type="openai_embedding",
                resource_name="text-embedding-ada-002",
                provider="openai"
            )
            
            # Verify lineage entry was created
            assert len(state.lineage) == 1
            entry = state.lineage[0]
            
            assert entry.action == "execute"
            assert entry.pipeline == "data_processing"
            assert entry.step == "embed_documents"
            assert entry.resource_type == "openai_embedding"
            assert entry.resource_name == "text-embedding-ada-002"
            assert entry.provider == "openai"
            assert entry.duration_ms == 3000
            assert entry.cost_usd == 0.02
    
    def test_record_destroy_action(self):
        """Test recording a destroy action in lineage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(state_dir=tmpdir, enable_lineage=True)
            state = manager.load("test_experiment")
            
            # Record a destroy action
            manager.record_destroy(
                resource_type="pinecone_index",
                resource_name="embeddings",
                provider="pinecone",
                input_data={"force": True},
                result={"deleted": True, "cleanup_time": "2025-10-05T15:30:00Z"},
                duration_ms=800,
                pipeline="cleanup",
                step="destroy_index"
            )
            
            # Verify lineage entry was created
            assert len(state.lineage) == 1
            entry = state.lineage[0]
            
            assert entry.action == "destroy"
            assert entry.resource_type == "pinecone_index"
            assert entry.resource_name == "embeddings"
            assert entry.provider == "pinecone"
            assert entry.pipeline == "cleanup"
            assert entry.step == "destroy_index"
            assert entry.duration_ms == 800
            assert entry.cost_usd is None  # No cost specified
    
    def test_multiple_actions_in_lineage(self):
        """Test that multiple actions are properly tracked in order."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(state_dir=tmpdir, enable_lineage=True)
            state = manager.load("test_experiment")
            
            # Record multiple actions
            manager.record_provision(
                resource_type="pinecone_index",
                resource_name="embeddings",
                provider="pinecone",
                input_data={"dimension": 1536},
                result={"id": "embeddings-abc123"},
                duration_ms=1500,
                cost_usd=0.05
            )
            
            manager.record_execution(
                pipeline="data_processing",
                step="embed_documents",
                input_data={"documents": ["doc1.txt"]},
                result={"embeddings_created": 1},
                duration_ms=2000,
                cost_usd=0.01
            )
            
            manager.record_destroy(
                resource_type="pinecone_index",
                resource_name="embeddings",
                provider="pinecone",
                input_data={"force": True},
                result={"deleted": True},
                duration_ms=800
            )
            
            # Verify all actions are tracked
            assert len(state.lineage) == 3
            assert state.lineage[0].action == "provision"
            assert state.lineage[1].action == "execute"
            assert state.lineage[2].action == "destroy"
            
            # Verify metadata is updated
            assert state.metadata['total_actions'] == 3
            assert state.metadata['total_cost_usd'] == 0.06  # 0.05 + 0.01 + 0 (destroy had no cost)
    
    def test_lineage_persistence(self):
        """Test that lineage is persisted to disk and loaded correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create state and add lineage
            manager1 = StateManager(state_dir=tmpdir, enable_lineage=True)
            state1 = manager1.load("test_experiment")
            
            manager1.record_provision(
                resource_type="test_resource",
                resource_name="example",
                provider="test_provider",
                input_data={"config": "value"},
                result={"id": "test-123"},
                duration_ms=100,
                cost_usd=0.01
            )
            
            # Save state
            saved_path = manager1.save()
            assert saved_path is not None
            assert saved_path.exists()
            
            # Load state in new manager
            manager2 = StateManager(state_dir=tmpdir, enable_lineage=True)
            state2 = manager2.load("test_experiment")
            
            # Verify lineage was persisted
            assert isinstance(state2, State)
            assert len(state2.lineage) == 1
            assert state2.lineage[0].action == "provision"
            assert state2.lineage[0].resource_type == "test_resource"
            assert state2.lineage[0].resource_name == "example"
            assert state2.lineage[0].provider == "test_provider"
            assert state2.lineage[0].duration_ms == 100
            assert state2.lineage[0].cost_usd == 0.01
    
    def test_lineage_json_structure(self):
        """Test that lineage is properly serialized to JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(state_dir=tmpdir, enable_lineage=True)
            state = manager.load("test_experiment")
            
            manager.record_provision(
                resource_type="test_resource",
                resource_name="example",
                provider="test_provider",
                input_data={"config": "value"},
                result={"id": "test-123"},
                duration_ms=100,
                cost_usd=0.01
            )
            
            # Save and read raw JSON
            manager.save()
            state_file = Path(tmpdir) / "test_experiment.tfstate"
            
            with open(state_file) as f:
                data = json.load(f)
            
            # Verify JSON structure
            assert "lineage" in data
            assert len(data["lineage"]) == 1
            
            lineage_entry = data["lineage"][0]
            assert lineage_entry["action"] == "provision"
            assert lineage_entry["resource_type"] == "test_resource"
            assert lineage_entry["resource_name"] == "example"
            assert lineage_entry["provider"] == "test_provider"
            assert lineage_entry["input"] == {"config": "value"}
            assert lineage_entry["result"] == {"id": "test-123"}
            assert lineage_entry["duration_ms"] == 100
            assert lineage_entry["cost_usd"] == 0.01
            assert "timestamp" in lineage_entry
    
    def test_action_timing(self):
        """Test automatic action timing functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(state_dir=tmpdir, enable_lineage=True)
            state = manager.load("test_experiment")
            
            # Start action timer
            manager.start_action()
            
            # Simulate some work (small delay)
            import time
            time.sleep(0.01)  # 10ms
            
            # Record action without explicit duration
            manager.record_provision(
                resource_type="test_resource",
                resource_name="example",
                provider="test_provider",
                input_data={"config": "value"},
                result={"id": "test-123"}
            )
            
            # Verify duration was automatically calculated
            assert len(state.lineage) == 1
            entry = state.lineage[0]
            assert entry.duration_ms >= 10  # Should be at least 10ms
            assert entry.duration_ms < 1000  # But not too long
    
    def test_diagnostics_tracking(self):
        """Test diagnostic message tracking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(state_dir=tmpdir, enable_lineage=True)
            state = manager.load("test_experiment")
            
            # Add diagnostics
            manager.add_diagnostic(Diagnostic(
                severity="info",
                message="Starting resource provisioning",
                source="StateManager.test"
            ))
            
            manager.add_diagnostic(Diagnostic(
                severity="warning",
                message="Resource took longer than expected",
                source="Provider.pinecone"
            ))
            
            # Verify diagnostics were added
            assert len(state.diagnostics) == 2
            assert state.diagnostics[0].severity == "info"
            assert state.diagnostics[0].message == "Starting resource provisioning"
            assert state.diagnostics[0].source == "StateManager.test"
            
            assert state.diagnostics[1].severity == "warning"
            assert state.diagnostics[1].message == "Resource took longer than expected"
            assert state.diagnostics[1].source == "Provider.pinecone"
    
    def test_lineage_summary(self):
        """Test lineage summary functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(state_dir=tmpdir, enable_lineage=True)
            state = manager.load("test_experiment")
            
            # Add various actions
            manager.record_provision(
                resource_type="pinecone_index",
                resource_name="embeddings",
                provider="pinecone",
                input_data={},
                result={},
                duration_ms=1500,
                cost_usd=0.05
            )
            
            manager.record_execution(
                pipeline="data_processing",
                step="embed_documents",
                input_data={},
                result={},
                duration_ms=2000,
                cost_usd=0.02
            )
            
            manager.record_provision(
                resource_type="openai_embedding",
                resource_name="ada-002",
                provider="openai",
                input_data={},
                result={},
                duration_ms=500,
                cost_usd=0.01
            )
            
            # Add diagnostic
            manager.add_diagnostic(Diagnostic(
                severity="info",
                message="Test diagnostic"
            ))
            
            # Get summary
            summary = manager.get_lineage_summary()
            
            assert summary["lineage_enabled"] is True
            assert summary["total_actions"] == 3
            assert summary["actions_by_type"]["provision"] == 2
            assert summary["actions_by_type"]["execute"] == 1
            assert summary["total_duration_ms"] == 4000  # 1500 + 2000 + 500
            assert summary["total_cost_usd"] == 0.08  # 0.05 + 0.02 + 0.01
            assert summary["diagnostics_count"] == 1


class TestLegacyCompatibility:
    """Test backwards compatibility with legacy StateFile format."""
    
    def test_legacy_state_without_lineage(self):
        """Test that legacy state works without lineage tracking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(state_dir=tmpdir, enable_lineage=False)
            state = manager.load("test_experiment")
            
            # Should be legacy StateFile, not State
            from src.aicl.state.models import StateFile
            assert isinstance(state, StateFile)
            assert not hasattr(state, 'lineage')
            
            # Legacy methods should still work
            resource = ResourceState(
                id="test-resource",
                type="test_type",
                provider="test_provider"
            )
            manager.add_resource(resource)
            
            # Lineage methods should not crash but do nothing
            manager.record_provision(
                resource_type="test",
                resource_name="test",
                provider="test",
                input_data={},
                result={}
            )
            
            # Summary should indicate lineage is disabled
            summary = manager.get_lineage_summary()
            assert summary["lineage_enabled"] is False
    
    def test_legacy_state_migration(self):
        """Test automatic migration from legacy to new format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create legacy state file manually
            legacy_data = {
                "version": "1.0",
                "experiment_id": "test_experiment",
                "resources": {
                    "test-resource": {
                        "id": "test-resource",
                        "type": "test_type",
                        "provider": "test_provider",
                        "attributes": {"key": "value"},
                        "metadata": {},
                        "status": "ready"
                    }
                },
                "outputs": {"output1": "value1"},
                "metadata": {
                    "created_at": "2025-10-05T10:00:00Z",
                    "last_modified": "2025-10-05T10:00:00Z"
                }
            }
            
            state_file = Path(tmpdir) / "test_experiment.tfstate"
            with open(state_file, 'w') as f:
                json.dump(legacy_data, f)
            
            # Load with lineage enabled - should migrate
            manager = StateManager(state_dir=tmpdir, enable_lineage=True)
            state = manager.load("test_experiment")
            
            # Should be migrated to new State format
            assert isinstance(state, State)
            assert hasattr(state, 'lineage')
            assert len(state.lineage) == 0  # Empty lineage for migrated state
            
            # Legacy data should be preserved
            assert state.experiment_id == "test_experiment"
            assert "test-resource" in state.resources
            assert state.resources["test-resource"].type == "test_type"
            assert state.outputs["output1"] == "value1"
            
            # Should have migration diagnostic
            assert len(state.diagnostics) == 1
            assert "migrated" in state.diagnostics[0].message.lower()


if __name__ == "__main__":
    pytest.main([__file__])
