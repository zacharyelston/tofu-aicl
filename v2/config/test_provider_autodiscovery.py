"""
Test Provider Auto-Discovery

Verifies that ProviderConfigLoader automatically discovers providers
from the providers/ directory without manual registration.
"""

import pytest
from pathlib import Path
from v2.config.provider_loader import ProviderConfigLoader


def test_autodiscovery_finds_all_providers():
    """Auto-discovery should find all providers in providers/ directory"""
    loader = ProviderConfigLoader()
    
    providers = loader.list_all()
    provider_names = [p.name for p in providers]
    
    # Verify key providers are discovered
    assert "openai" in provider_names
    assert "naga" in provider_names
    assert "openrouter" in provider_names
    assert "pinecone" in provider_names
    assert "ragie" in provider_names
    
    # Should have all 9 providers
    assert len(providers) >= 9


def test_autodiscovery_no_manual_registration():
    """Providers are discovered without manual registration code"""
    loader = ProviderConfigLoader()
    
    # No register() calls needed - just instantiate
    openai = loader.get("openai")
    assert openai is not None
    assert openai.name == "openai"


def test_autodiscovery_scans_directory():
    """Auto-discovery scans providers/ directory for config.yaml"""
    providers_dir = Path(__file__).parent.parent.parent / "providers"
    assert providers_dir.exists()
    
    loader = ProviderConfigLoader(providers_dir=providers_dir)
    
    # Count config files
    config_files = list(providers_dir.glob("*/config.yaml"))
    discovered_providers = loader.list_all()
    
    assert len(discovered_providers) == len(config_files)


def test_new_provider_autodiscovered(tmp_path):
    """Adding a new provider folder makes it immediately available"""
    # Create a temporary providers directory
    test_providers_dir = tmp_path / "providers"
    test_providers_dir.mkdir()
    
    # Create a test provider
    test_provider_dir = test_providers_dir / "test_provider"
    test_provider_dir.mkdir()
    
    config_content = """
provider:
  name: test_provider
  display_name: Test Provider
  version: 1.0.0
  source: aicl/test
  description: Auto-discovered test provider
  
  runtime:
    entrypoint: server.py
    default_port: 60000
    mode: subprocess
  
  environment:
    required_vars: []
  
  capabilities:
    types: [test]
    operations: [test_op]
  
  model_ids: []
"""
    
    config_file = test_provider_dir / "config.yaml"
    config_file.write_text(config_content)
    
    # Load with auto-discovery
    loader = ProviderConfigLoader(providers_dir=test_providers_dir)
    
    # Verify it was discovered
    assert loader.get("test_provider") is not None
    assert loader.get("test_provider").display_name == "Test Provider"
    assert len(loader.list_all()) == 1


def test_autodiscovery_handles_missing_directory():
    """Auto-discovery fails gracefully if directory missing"""
    with pytest.raises(ValueError, match="Providers directory not found"):
        ProviderConfigLoader(providers_dir=Path("/nonexistent"))


def test_autodiscovery_skips_invalid_configs(tmp_path):
    """Auto-discovery skips directories without config.yaml"""
    test_providers_dir = tmp_path / "providers"
    test_providers_dir.mkdir()
    
    # Create directory without config.yaml
    empty_dir = test_providers_dir / "empty"
    empty_dir.mkdir()
    
    # Create directory with config.yaml
    valid_dir = test_providers_dir / "valid"
    valid_dir.mkdir()
    (valid_dir / "config.yaml").write_text("""
provider:
  name: valid
  display_name: Valid
  version: 1.0.0
  source: aicl/valid
  description: Valid provider
  runtime:
    entrypoint: server.py
    default_port: 60001
    mode: subprocess
  environment:
    required_vars: []
  capabilities:
    types: []
  model_ids: []
""")
    
    loader = ProviderConfigLoader(providers_dir=test_providers_dir)
    
    # Should only find 1 provider (empty_dir skipped)
    assert len(loader.list_all()) == 1
    assert loader.get("valid") is not None
    assert loader.get("empty") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
