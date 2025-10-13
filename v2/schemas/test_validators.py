"""
Tests for Schema Validators

Validates provider and model schema validation.
"""

import pytest
from v2.schemas.validators import (
    validate_provider_config,
    validate_model_config,
    ValidationError
)


class TestProviderValidation:
    """Test provider config validation"""
    
    def test_valid_provider_config(self):
        """Valid provider config passes validation"""
        config = {
            'provider': {
                'name': 'test_provider',
                'display_name': 'Test Provider',
                'version': '1.0.0',
                'source': 'test/provider',
                'description': 'Test provider for validation',
                'runtime': {
                    'entrypoint': 'server.py',
                    'default_port': 50051,
                    'mode': 'both'
                },
                'docker': {
                    'image': 'test/provider:latest',
                    'internal_port': 50051
                },
                'environment': {
                    'required_vars': ['API_KEY']
                },
                'capabilities': {
                    'types': ['llm']
                }
            }
        }
        result = validate_provider_config(config)
        assert result.name == 'test_provider'
        assert result.runtime.default_port == 50051
        assert result.runtime.mode.value == 'both'
    
    def test_invalid_runtime_mode_fails(self):
        """Invalid runtime mode raises error"""
        config = {
            'provider': {
                'name': 'test',
                'display_name': 'Test',
                'version': '1.0.0',
                'runtime': {
                    'entrypoint': 'server.py',
                    'default_port': 50051,
                    'mode': 'invalid_mode'  # Invalid!
                },
                'environment': {'required_vars': []},
                'capabilities': {'types': ['llm']}
            }
        }
        with pytest.raises((ValidationError, ValueError)):
            validate_provider_config(config)
    
    def test_missing_required_field_fails(self):
        """Missing required fields raise errors"""
        config = {
            'provider': {
                'name': 'test',
                # Missing 'display_name'
                'version': '1.0.0',
                'runtime': {
                    'entrypoint': 'server.py',
                    'default_port': 50051,
                    'mode': 'both'
                },
                'environment': {'required_vars': []},
                'capabilities': {'types': ['llm']}
            }
        }
        with pytest.raises((ValidationError, ValueError)):
            validate_provider_config(config)
    
    def test_invalid_port_fails(self):
        """Invalid port number raises error"""
        config = {
            'provider': {
                'name': 'test',
                'display_name': 'Test',
                'version': '1.0.0',
                'runtime': {
                    'entrypoint': 'server.py',
                    'default_port': 70000,  # Out of range!
                    'mode': 'both'
                },
                'environment': {'required_vars': []},
                'capabilities': {'types': ['llm']}
            }
        }
        with pytest.raises((ValidationError, ValueError)):
            validate_provider_config(config)


class TestModelValidation:
    """Test model config validation"""
    
    def test_valid_model_config(self):
        """Valid model config passes validation"""
        config = {
            'id': 'gpt-4o',  # Required field
            'name': 'gpt-4o',
            'display_name': 'GPT-4o',  # Required field
            'provider': 'openai',
            'type': 'chat',
            'cost_per_1k_input': 0.0025,
            'cost_per_1k_output': 0.01,
            'quality_score': 9.5,
            'context_window': 128000
        }
        result = validate_model_config(config)
        assert result.name == 'gpt-4o'
        assert result.provider == 'openai'
        assert result.quality_score == 9.5
    
    def test_invalid_model_type_fails(self):
        """Invalid model type raises error"""
        config = {
            'name': 'test-model',
            'provider': 'test',
            'type': 'invalid_type',  # Invalid!
            'cost_per_1k_input': 0.001,
            'quality_score': 5.0
        }
        with pytest.raises((ValidationError, ValueError)):
            validate_model_config(config)
    
    def test_negative_cost_fails(self):
        """Negative cost raises error"""
        config = {
            'name': 'test-model',
            'provider': 'test',
            'type': 'chat',
            'cost_per_1k_input': -0.001,  # Negative!
            'quality_score': 5.0
        }
        with pytest.raises((ValidationError, ValueError)):
            validate_model_config(config)
    
    def test_quality_score_out_of_range_fails(self):
        """Quality score outside 0-10 range fails"""
        config = {
            'name': 'test-model',
            'provider': 'test',
            'type': 'chat',
            'cost_per_1k_input': 0.001,
            'quality_score': 15.0  # Out of range!
        }
        with pytest.raises((ValidationError, ValueError)):
            validate_model_config(config)
    
    def test_missing_required_field_fails(self):
        """Missing required fields raise errors"""
        config = {
            'name': 'test-model',
            'provider': 'test',
            # Missing 'type'
            'cost_per_1k_input': 0.001,
            'quality_score': 5.0
        }
        with pytest.raises((ValidationError, ValueError)):
            validate_model_config(config)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
