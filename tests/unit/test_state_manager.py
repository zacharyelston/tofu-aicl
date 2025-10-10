import pytest
from src.aicl.state.manager import StateManager, ResourceState, StateFile
import tempfile
import json
import os

class TestStateManager:
    
    def test_state_manager_initialization(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(tmpdir)
            assert manager.state_dir.exists()
    
    def test_add_resource(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(tmpdir)
            manager.load('test')
            
            resource = ResourceState(
                id='test-resource',
                type='test_type',
                provider='test_provider',
                attributes={'key': 'value'},
                metadata={},
                status='created'
            )
            
            manager.add_resource(resource)
            
            assert 'test-resource' in manager.current_state.resources
            assert manager.current_state.resources['test-resource'].attributes['key'] == 'value'
    
    def test_get_resource(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(tmpdir)
            manager.load('test')
            
            resource = ResourceState(
                id='test-resource',
                type='test_type',
                provider='test_provider',
                attributes={'key': 'value'},
                metadata={},
                status='created'
            )
            
            manager.add_resource(resource)
            retrieved = manager.get_resource('test-resource')
            
            assert retrieved is not None
            assert retrieved.id == 'test-resource'
            assert retrieved.attributes['key'] == 'value'
    
    def test_remove_resource(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(tmpdir)
            manager.load('test')
            
            resource = ResourceState(
                id='test-resource',
                type='test_type',
                provider='test_provider',
                attributes={},
                metadata={},
                status='created'
            )
            
            manager.add_resource(resource)
            assert 'test-resource' in manager.current_state.resources
            
            manager.remove_resource('test-resource')
            assert 'test-resource' not in manager.current_state.resources
    
    def test_save_and_load_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manager1 = StateManager(tmpdir)
            manager1.load('test')
            
            resource = ResourceState(
                id='test-resource',
                type='test_type',
                provider='test_provider',
                attributes={'key': 'value'},
                metadata={'source': 'test'},
                status='created'
            )
            manager1.add_resource(resource)
            manager1.save()
            
            manager2 = StateManager(tmpdir)
            manager2.load('test')
            
            assert 'test-resource' in manager2.current_state.resources
            assert manager2.current_state.resources['test-resource'].attributes['key'] == 'value'
