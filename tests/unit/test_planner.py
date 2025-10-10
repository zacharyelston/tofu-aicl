import pytest
from src.aicl.planner import Planner

class TestPlanner:
    
    def test_simple_dependency_order(self):
        parsed_config = {
            'resource': [
                {
                    'splitter_text': {
                        'chunks': {
                            'text': '${resource.loader_files.docs.attributes.content}',
                            'aiclResourceName': 'chunks'
                        }
                    }
                },
                {
                    'loader_files': {
                        'docs': {
                            'path': 'src/aicl',
                            'aiclResourceName': 'docs'
                        }
                    }
                }
            ]
        }
        
        planner = Planner(parsed_config)
        sorted_order, resource_map = planner.build_graph()
        
        assert len(sorted_order) == 2
        assert sorted_order[0] == 'loader_files.docs'
        assert sorted_order[1] == 'splitter_text.chunks'
    
    def test_no_dependencies(self):
        parsed_config = {
            'resource': [
                {
                    'loader_files': {
                        'docs1': {'path': 'src', 'aiclResourceName': 'docs1'}
                    }
                },
                {
                    'loader_files': {
                        'docs2': {'path': 'tests', 'aiclResourceName': 'docs2'}
                    }
                }
            ]
        }
        
        planner = Planner(parsed_config)
        sorted_order, resource_map = planner.build_graph()
        
        assert len(sorted_order) == 2
        assert 'loader_files.docs1' in sorted_order
        assert 'loader_files.docs2' in sorted_order
    
    def test_extract_resource_references(self):
        planner = Planner({})
        
        config = {
            'text': '${resource.loader_files.docs.attributes.content}',
            'nested': {
                'value': '${resource.splitter_text.chunks.attributes.result}'
            }
        }
        
        refs = planner._extract_resource_references(config)
        
        assert 'loader_files.docs' in refs
        assert 'splitter_text.chunks' in refs
    
    def test_circular_dependency_detection(self):
        parsed_config = {
            'resource': [
                {
                    'resource_a': {
                        'item1': {
                            'dep': '${resource.resource_b.item2.attributes.value}',
                            'aiclResourceName': 'item1'
                        }
                    }
                },
                {
                    'resource_b': {
                        'item2': {
                            'dep': '${resource.resource_a.item1.attributes.value}',
                            'aiclResourceName': 'item2'
                        }
                    }
                }
            ]
        }
        
        planner = Planner(parsed_config)
        
        with pytest.raises(Exception, match="Cycle detected"):
            planner.build_graph()
