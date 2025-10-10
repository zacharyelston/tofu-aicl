import pytest
from src.aicl.evaluator import HCLEvaluator
from src.aicl.state.manager import StateManager
import tempfile
import os

class TestHCLEvaluator:
    
    def test_evaluator_initialization(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_manager = StateManager(tmpdir)
            state_manager.load('test')
            evaluator = HCLEvaluator(state_manager)
            assert evaluator.state_manager == state_manager
    
    def test_simple_variable_interpolation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_manager = StateManager(tmpdir)
            state_manager.load('test')
            
            parsed_config = {
                'variable': [
                    {'test_var': {'default': 'test_value'}}
                ]
            }
            evaluator = HCLEvaluator(state_manager, parsed_config)
            context = evaluator.build_context()
            
            result = evaluator.resolve_value('${var.test_var}', context)
            assert result == 'test_value'
    
    def test_resource_attribute_interpolation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_manager = StateManager(tmpdir)
            state_manager.load('test')
            
            from src.aicl.state.manager import ResourceState
            resource = ResourceState(
                id='loader_files-docs',
                type='loader_files',
                provider='loader',
                attributes={'files': ['file1.py', 'file2.py']},
                metadata={},
                status='created'
            )
            state_manager.add_resource(resource)
            
            evaluator = HCLEvaluator(state_manager)
            context = evaluator.build_context()
            
            result = evaluator.resolve_value('${resource.loader_files.docs.attributes.files}', context)
            assert result == ['file1.py', 'file2.py']
    
    def test_nested_dict_evaluation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_manager = StateManager(tmpdir)
            state_manager.load('test')
            
            parsed_config = {
                'variable': [
                    {'path': {'default': 'src/aicl'}}
                ]
            }
            evaluator = HCLEvaluator(state_manager, parsed_config)
            context = evaluator.build_context()
            
            config = {
                'path': '${var.path}',
                'nested': {
                    'value': '${var.path}/nested'
                }
            }
            
            result = evaluator.resolve_config(config, context)
            assert result['path'] == 'src/aicl'
            assert result['nested']['value'] == 'src/aicl/nested'
    
    def test_no_interpolation_needed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_manager = StateManager(tmpdir)
            state_manager.load('test')
            evaluator = HCLEvaluator(state_manager)
            context = evaluator.build_context()
            
            result = evaluator.resolve_value('plain string', context)
            assert result == 'plain string'
    
    def test_missing_variable_returns_original(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_manager = StateManager(tmpdir)
            state_manager.load('test')
            evaluator = HCLEvaluator(state_manager)
            context = evaluator.build_context()
            
            result = evaluator.resolve_value('${var.missing}', context)
            assert result == '${var.missing}'
