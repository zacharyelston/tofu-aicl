import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def sample_hcl_config():
    return {
        'variable': [
            {'test_var': {'type': 'string', 'default': 'test_value'}}
        ],
        'provider': [
            {'loader': {'source': 'aicl/file_loader'}}
        ],
        'resource': [
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

@pytest.fixture
def sample_state():
    from src.aicl.state.manager import ResourceState
    
    return ResourceState(
        id='loader_files-docs',
        type='loader_files',
        provider='loader',
        attributes={'files': ['file1.py', 'file2.py']},
        metadata={'source': 'test'},
        status='created'
    )
