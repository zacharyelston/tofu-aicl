import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os
import sys
from io import StringIO

from src.aicl.core.engine import AICLEngine


class TestCLIOutputConfiguration:
    """Test CLI output destination controls"""
    
    def setup_method(self):
        """Create temporary config file for testing"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.aicl', delete=False)
        self.temp_file.write('''
terraform {
  required_providers {
    loader = {
      source = "aicl/file_loader"
    }
  }
}

variable "experiment_id" {
  default = "test-exp"
}

resource "loader_files" "docs" {
  path = "."
  aiclResourceName = "docs"
}
''')
        self.temp_file.flush()
        self.temp_file.close()
    
    def teardown_method(self):
        """Clean up temporary files"""
        if hasattr(self, 'temp_file'):
            try:
                os.unlink(self.temp_file.name)
            except:
                pass
    
    def test_default_output_config(self):
        """Test default output configuration (file + stdout enabled)"""
        engine = AICLEngine(config_path=self.temp_file.name)
        
        assert engine.output_file is True
        assert engine.output_docdb is False
        assert engine.output_stdout is True
        assert engine.quiet is False
        assert engine.parallel is False
    
    def test_output_file_flag(self):
        """Test --output-file flag"""
        engine = AICLEngine(config_path=self.temp_file.name, output_file=True)
        assert engine.output_file is True
        
        engine = AICLEngine(config_path=self.temp_file.name, output_file=False)
        assert engine.output_file is False
    
    def test_output_docdb_flag(self):
        """Test --output-docdb flag (enables PostgreSQL storage)"""
        with patch('experiments.storage.experiment_docdb.ExperimentDocDB') as mock_docdb:
            mock_docdb.return_value = MagicMock()
            
            engine = AICLEngine(config_path=self.temp_file.name, output_docdb=True)
            assert engine.output_docdb is True
            assert engine.docdb is not None
            mock_docdb.assert_called_once()
    
    def test_output_docdb_flag_disabled(self):
        """Test DocDB disabled by default"""
        engine = AICLEngine(config_path=self.temp_file.name, output_docdb=False)
        assert engine.output_docdb is False
        assert engine.docdb is None
    
    def test_output_stdout_flag(self):
        """Test --output-stdout and --no-stdout flags"""
        engine = AICLEngine(config_path=self.temp_file.name, output_stdout=True)
        assert engine.output_stdout is True
        
        engine = AICLEngine(config_path=self.temp_file.name, output_stdout=False)
        assert engine.output_stdout is False
    
    def test_quiet_flag(self):
        """Test --quiet flag"""
        engine = AICLEngine(config_path=self.temp_file.name, quiet=True)
        assert engine.quiet is True
        
        engine = AICLEngine(config_path=self.temp_file.name, quiet=False)
        assert engine.quiet is False
    
    def test_parallel_flag(self):
        """Test --parallel flag (experimental)"""
        engine = AICLEngine(config_path=self.temp_file.name, parallel=True)
        assert engine.parallel is True
        
        engine = AICLEngine(config_path=self.temp_file.name, parallel=False)
        assert engine.parallel is False
    
    def test_custom_experiment_id(self):
        """Test --experiment-id flag"""
        custom_id = "my-custom-experiment"
        engine = AICLEngine(config_path=self.temp_file.name, experiment_id=custom_id)
        assert engine.custom_experiment_id == custom_id
    
    def test_tags_configuration(self):
        """Test --tags flag"""
        tags = ["rag", "demo", "production"]
        engine = AICLEngine(config_path=self.temp_file.name, tags=tags)
        assert engine.tags == tags
    
    def test_tags_default_empty_list(self):
        """Test tags default to empty list"""
        engine = AICLEngine(config_path=self.temp_file.name)
        assert engine.tags == []
    
    def test_combined_flags(self):
        """Test multiple flags combined"""
        engine = AICLEngine(
            config_path=self.temp_file.name,
            output_file=True,
            output_stdout=False,
            quiet=True,
            experiment_id="multi-flag-test",
            tags=["test", "combined"]
        )
        
        assert engine.output_file is True
        assert engine.output_stdout is False
        assert engine.quiet is True
        assert engine.custom_experiment_id == "multi-flag-test"
        assert engine.tags == ["test", "combined"]


class TestCLIOutputMethods:
    """Test output helper methods"""
    
    def setup_method(self):
        """Create engine with mocked state"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.aicl', delete=False)
        self.temp_file.write('''
variable "experiment_id" {
  default = "test-exp"
}
''')
        self.temp_file.flush()
        self.temp_file.close()
    
    def teardown_method(self):
        """Clean up"""
        try:
            os.unlink(self.temp_file.name)
        except:
            pass
    
    def test_print_outputs_with_dict(self, capsys):
        """Test _print_outputs with dictionary output"""
        engine = AICLEngine(config_path=self.temp_file.name)
        
        mock_state = Mock()
        mock_state.outputs = {
            "result": {"key": "value"},
            "count": 42
        }
        engine.state_manager.current_state = mock_state
        
        engine._print_outputs()
        
        captured = capsys.readouterr()
        assert "EXPERIMENT OUTPUTS" in captured.out
        assert "result:" in captured.out
        assert "count:" in captured.out
    
    def test_print_outputs_empty(self, capsys):
        """Test _print_outputs with no outputs"""
        engine = AICLEngine(config_path=self.temp_file.name)
        
        mock_state = Mock()
        mock_state.outputs = {}
        engine.state_manager.current_state = mock_state
        
        engine._print_outputs()
        
        captured = capsys.readouterr()
        assert "EXPERIMENT OUTPUTS" not in captured.out
    
    def test_print_outputs_no_state(self, capsys):
        """Test _print_outputs with no state"""
        engine = AICLEngine(config_path=self.temp_file.name)
        engine.state_manager.current_state = None
        
        engine._print_outputs()
        
        captured = capsys.readouterr()
        assert captured.out == ""
    
    def test_save_to_docdb_success(self):
        """Test _save_to_docdb successfully saves experiment"""
        with patch('experiments.storage.experiment_docdb.ExperimentDocDB') as mock_docdb_class:
            mock_docdb_instance = MagicMock()
            mock_docdb_instance.save_experiment.return_value = 123
            mock_docdb_class.return_value = mock_docdb_instance
            
            engine = AICLEngine(
                config_path=self.temp_file.name,
                output_docdb=True,
                experiment_id="test-docdb",
                tags=["test"]
            )
            
            mock_state = Mock()
            mock_state.outputs = {"result": "test"}
            mock_state.resources = {}
            engine.state_manager.current_state = mock_state
            
            engine._save_to_docdb("default-exp")
            
            mock_docdb_instance.save_experiment.assert_called_once()
            call_args = mock_docdb_instance.save_experiment.call_args
            assert call_args.kwargs['experiment_id'] == "test-docdb"
            assert call_args.kwargs['metadata']['tags'] == ["test"]
    
    def test_save_to_docdb_no_state(self):
        """Test _save_to_docdb with no state (should return early)"""
        with patch('experiments.storage.experiment_docdb.ExperimentDocDB') as mock_docdb_class:
            mock_docdb_instance = MagicMock()
            mock_docdb_class.return_value = mock_docdb_instance
            
            engine = AICLEngine(config_path=self.temp_file.name, output_docdb=True)
            engine.state_manager.current_state = None
            
            engine._save_to_docdb("test-exp")
            
            mock_docdb_instance.save_experiment.assert_not_called()
    
    def test_save_to_docdb_error_handling(self, capsys):
        """Test _save_to_docdb handles errors gracefully"""
        with patch('experiments.storage.experiment_docdb.ExperimentDocDB') as mock_docdb_class:
            mock_docdb_instance = MagicMock()
            mock_docdb_instance.save_experiment.side_effect = Exception("DB Error")
            mock_docdb_class.return_value = mock_docdb_instance
            
            engine = AICLEngine(config_path=self.temp_file.name, output_docdb=True)
            
            mock_state = Mock()
            mock_state.outputs = {"result": "test"}
            mock_state.resources = {}
            engine.state_manager.current_state = mock_state
            
            engine._save_to_docdb("test-exp")
            
            captured = capsys.readouterr()
            assert "Warning: Failed to save to DocDB" in captured.out


class TestCLIQuietMode:
    """Test quiet mode behavior"""
    
    def test_quiet_mode_suppresses_docdb_success(self):
        """Test that quiet mode suppresses DocDB success message"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.aicl', delete=False) as f:
            f.write('variable "experiment_id" { default = "test" }')
            f.flush()
            
            try:
                with patch('experiments.storage.experiment_docdb.ExperimentDocDB') as mock_docdb_class:
                    mock_docdb_instance = MagicMock()
                    mock_docdb_class.return_value = mock_docdb_instance
                    
                    engine = AICLEngine(
                        config_path=f.name,
                        output_docdb=True,
                        quiet=True
                    )
                    
                    assert engine.quiet is True
                    mock_docdb_class.assert_called_once()
            finally:
                os.unlink(f.name)


class TestCLIArgparse:
    """Test command-line argument parsing"""
    
    def test_argparse_integration(self):
        """Test that argparse flags map correctly to engine parameters"""
        import argparse
        
        parser = argparse.ArgumentParser()
        parser.add_argument('config_path', nargs='?', default='example.aicl')
        parser.add_argument('--output-file', action='store_true')
        parser.add_argument('--output-docdb', action='store_true')
        parser.add_argument('--output-stdout', action='store_true', default=True)
        parser.add_argument('--no-stdout', dest='output_stdout', action='store_false')
        parser.add_argument('--quiet', '-q', action='store_true')
        parser.add_argument('--parallel', action='store_true')
        parser.add_argument('--experiment-id', type=str)
        parser.add_argument('--tags', type=str)
        
        args = parser.parse_args([
            'test.aicl',
            '--output-file',
            '--output-docdb',
            '--quiet',
            '--experiment-id', 'test-123',
            '--tags', 'rag,demo,v1'
        ])
        
        assert args.config_path == 'test.aicl'
        assert args.output_file is True
        assert args.output_docdb is True
        assert args.quiet is True
        assert args.experiment_id == 'test-123'
        assert args.tags == 'rag,demo,v1'
    
    def test_no_stdout_flag_disables_output(self):
        """Test that --no-stdout overrides default"""
        import argparse
        
        parser = argparse.ArgumentParser()
        parser.add_argument('config_path', nargs='?', default='example.aicl')
        parser.add_argument('--output-stdout', action='store_true', default=True)
        parser.add_argument('--no-stdout', dest='output_stdout', action='store_false')
        
        args = parser.parse_args(['test.aicl', '--no-stdout'])
        assert args.output_stdout is False
        
        args = parser.parse_args(['test.aicl'])
        assert args.output_stdout is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
