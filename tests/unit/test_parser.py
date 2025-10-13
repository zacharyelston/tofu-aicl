import pytest
from src.aicl.parser import HCLParser
from pathlib import Path
import tempfile
import os

class TestHCLParser:
    
    def test_parser_initialization(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.aicl', delete=False) as f:
            f.write('resource "test" "example" { value = "test" }')
            f.flush()
            
            try:
                parser = HCLParser(f.name)
                assert parser.file_path == f.name
            finally:
                os.unlink(f.name)
    
    def test_parse_simple_resource(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.aicl', delete=False) as f:
            f.write('''
resource "loader_files" "docs" {
  path = "src/aicl"
  aiclResourceName = "docs"
}
''')
            f.flush()
            
            try:
                parser = HCLParser(f.name)
                config = parser.parse()
                
                assert 'resource' in config
                assert len(config['resource']) == 1
                assert 'loader_files' in config['resource'][0]
                assert 'docs' in config['resource'][0]['loader_files']
            finally:
                os.unlink(f.name)
    
    def test_parse_variables(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.aicl', delete=False) as f:
            f.write('''
variable "test_var" {
  type    = "string"
  default = "test_value"
}
''')
            f.flush()
            
            try:
                parser = HCLParser(f.name)
                config = parser.parse()
                
                assert 'variable' in config
                assert len(config['variable']) == 1
                assert 'test_var' in config['variable'][0]
                assert config['variable'][0]['test_var']['default'] == 'test_value'
            finally:
                os.unlink(f.name)
    
    def test_parse_provider(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.aicl', delete=False) as f:
            f.write('''
provider "loader" {
  source = "aicl/file_loader"
}
''')
            f.flush()
            
            try:
                parser = HCLParser(f.name)
                config = parser.parse()
                
                assert 'provider' in config
                assert len(config['provider']) == 1
                assert 'loader' in config['provider'][0]
            finally:
                os.unlink(f.name)
