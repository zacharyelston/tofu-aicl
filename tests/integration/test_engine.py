import pytest
from src.aicl.core.engine import AICLEngine
from pathlib import Path
import tempfile
import os

class TestAICLEngine:
    
    def test_engine_initialization(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.aicl', delete=False) as f:
            f.write('resource "test" "example" { value = "test" }')
            f.flush()
            
            try:
                engine = AICLEngine(config_path=f.name)
                assert engine.config_path == Path(f.name)
            finally:
                os.unlink(f.name)
    
    def test_parse_config(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.aicl', delete=False) as f:
            f.write('''
provider "loader" {
  source = "aicl/file_loader"
}

resource "loader_files" "docs" {
  path = "src/aicl"
  aiclResourceName = "docs"
}
''')
            f.flush()
            
            try:
                engine = AICLEngine(config_path=f.name)
                config = engine._parse_config()
                
                assert 'provider' in config
                assert 'resource' in config
                assert len(config['provider']) == 1
                assert len(config['resource']) == 1
            finally:
                os.unlink(f.name)

@pytest.mark.skip(reason="Requires provider infrastructure")
class TestEngineWithProviders:
    
    def test_full_workflow(self):
        pass
