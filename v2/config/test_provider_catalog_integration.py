"""
Test integration between ProviderConfigLoader and ModelCatalog

Verifies that providers correctly reference models from centralized catalog
instead of duplicating model definitions.
"""

import pytest
from v2.config.provider_loader import ProviderConfigLoader
from v2.config.model_catalog import ModelCatalog


def test_provider_has_model_catalog_reference():
    """Provider configs should have access to centralized ModelCatalog"""
    loader = ProviderConfigLoader()
    openai_config = loader.get("openai")
    
    assert openai_config is not None
    assert openai_config._model_catalog is not None
    assert isinstance(openai_config._model_catalog, ModelCatalog)


def test_provider_get_model_from_catalog():
    """Providers should retrieve models from centralized catalog"""
    loader = ProviderConfigLoader()
    openai_config = loader.get("openai")
    
    # Get model from catalog
    model = openai_config.get_model("gpt-4o")
    
    assert model is not None
    assert model.id == "gpt-4o"
    assert model.provider == "openai"
    assert model.type == "chat"
    assert model.quality_score == 9.5


def test_provider_get_all_models():
    """Providers should list all their models from catalog"""
    loader = ProviderConfigLoader()
    openai_config = loader.get("openai")
    
    models = openai_config.get_all_models()
    
    assert len(models) > 0
    model_ids = [m.id for m in models]
    assert "gpt-4o" in model_ids
    assert "text-embedding-3-small" in model_ids


def test_multiple_providers_share_catalog():
    """All providers should reference the same catalog instance"""
    loader = ProviderConfigLoader()
    
    openai_config = loader.get("openai")
    naga_config = loader.get("naga")
    
    # Same catalog instance
    assert openai_config._model_catalog is naga_config._model_catalog


def test_openai_models_from_catalog():
    """OpenAI provider should use model_ids from catalog"""
    loader = ProviderConfigLoader()
    config = loader.get("openai")
    
    assert len(config.model_ids) > 0
    assert "gpt-4o" in config.model_ids
    assert "text-embedding-3-small" in config.model_ids
    
    # Legacy models should be empty
    assert len(config.models) == 0


def test_naga_models_from_catalog():
    """Naga provider should use model_ids from catalog"""
    loader = ProviderConfigLoader()
    config = loader.get("naga")
    
    assert len(config.model_ids) > 0
    assert "naga-qwen-72b" in config.model_ids
    assert "naga-text-embedding-3-small" in config.model_ids
    
    # Legacy models should be empty
    assert len(config.models) == 0


def test_openrouter_models_from_catalog():
    """OpenRouter provider should use model_ids from catalog"""
    loader = ProviderConfigLoader()
    config = loader.get("openrouter")
    
    assert len(config.model_ids) > 0
    assert "openrouter-claude-sonnet" in config.model_ids
    assert "openrouter-mistral-large" in config.model_ids
    
    # Legacy models should be empty
    assert len(config.models) == 0


def test_model_not_found_returns_none():
    """Getting non-existent model should return None"""
    loader = ProviderConfigLoader()
    config = loader.get("openai")
    
    model = config.get_model("non-existent-model")
    assert model is None


def test_all_model_ids_exist_in_catalog():
    """All provider model_ids should exist in ModelCatalog"""
    loader = ProviderConfigLoader()
    catalog = ModelCatalog()
    
    for provider_config in loader.list_all():
        for model_id in provider_config.model_ids:
            model = catalog.get(model_id)
            assert model is not None, f"Model {model_id} not found in catalog (referenced by {provider_config.name})"
            assert model.provider == provider_config.name, f"Model {model_id} provider mismatch"


def test_no_duplicate_model_definitions():
    """Providers should not duplicate model metadata"""
    loader = ProviderConfigLoader()
    
    for provider_config in loader.list_all():
        if provider_config.model_ids:
            # If using model_ids, should not have legacy models
            assert len(provider_config.models) == 0, (
                f"Provider {provider_config.name} has both model_ids and legacy models. "
                "Remove duplicate models field."
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
