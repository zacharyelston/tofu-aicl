"""
Tests for Model Catalog

Validates model loading, querying, filtering, and recommendations.
"""

import pytest
from v2.config.model_catalog import ModelCatalog


class TestModelCatalog:
    """Test suite for centralized model catalog"""
    
    @pytest.fixture
    def catalog(self):
        """Load catalog for tests"""
        return ModelCatalog()
    
    def test_catalog_loads_successfully(self, catalog):
        """Verify catalog loads without errors"""
        assert catalog is not None
        assert len(catalog) > 0
    
    def test_all_models_have_required_fields(self, catalog):
        """Ensure all models have required metadata"""
        for model in catalog.list_all():
            assert hasattr(model, 'name')
            assert hasattr(model, 'provider')
            assert hasattr(model, 'type')
            assert hasattr(model, 'cost_per_1k_input')
            assert hasattr(model, 'quality_score')
    
    def test_get_model_by_name(self, catalog):
        """Test fetching specific model"""
        gpt4 = catalog.get('gpt-4o')
        assert gpt4 is not None
        assert gpt4.name == 'gpt-4o'
        assert gpt4.provider == 'openai'
        
    def test_get_nonexistent_model_returns_none(self, catalog):
        """Test fetching non-existent model"""
        result = catalog.get('fake-model-xyz')
        assert result is None
    
    def test_filter_by_type(self, catalog):
        """Test filtering models by type"""
        chat_models = catalog.list_by_type('chat')
        assert len(chat_models) > 0
        assert all(m.type == 'chat' for m in chat_models)
        
        embedding_models = catalog.list_by_type('embedding')
        assert len(embedding_models) > 0
        assert all(m.type == 'embedding' for m in embedding_models)
    
    def test_filter_by_provider(self, catalog):
        """Test filtering models by provider"""
        openai_models = catalog.list_by_provider('openai')
        assert len(openai_models) > 0
        assert all(m.provider == 'openai' for m in openai_models)
        
        naga_models = catalog.list_by_provider('naga')
        assert len(naga_models) > 0
        assert all(m.provider == 'naga' for m in naga_models)
    
    def test_filter_by_max_cost(self, catalog):
        """Test cost filtering"""
        cheap_models = catalog.filter_by_cost(max_cost_per_1k=0.001)
        assert len(cheap_models) > 0
        assert all(m.cost_per_1k_input <= 0.001 for m in cheap_models)
    
    def test_filter_by_min_quality(self, catalog):
        """Test quality filtering"""
        high_quality = catalog.filter_by_cost(min_quality=8.0)
        assert len(high_quality) > 0
        assert all(m.quality_score >= 8.0 for m in high_quality)
    
    def test_combined_filters(self, catalog):
        """Test multiple filters together"""
        chat_models = catalog.list_by_type('chat')
        naga_chat = [m for m in chat_models if m.provider == 'naga']
        cheap_naga = [m for m in naga_chat if m.cost_per_1k_input <= 0.002]
        
        assert len(cheap_naga) > 0
        for model in cheap_naga:
            assert model.type == 'chat'
            assert model.provider == 'naga'
            assert model.cost_per_1k_input <= 0.002
    
    def test_get_best_value_model(self, catalog):
        """Test finding best value (quality >= 7, lowest cost)"""
        best_value = catalog.get_best_value('chat')
        assert best_value is not None
        assert best_value.quality_score >= 7.0
        
        # Verify it's the cheapest among quality >= 7 models
        quality_models = [
            m for m in catalog.list_by_type('chat')
            if m.quality_score >= 7.0
        ]
        min_cost = min(m.cost_per_1k_input for m in quality_models)
        assert best_value.cost_per_1k_input == min_cost
    
    def test_recommended_models(self, catalog):
        """Validate recommended models"""
        # Test getting recommended models for different categories
        chat_recommended = catalog.get_recommended('chat')
        assert isinstance(chat_recommended, list)
        
        embedding_recommended = catalog.get_recommended('embedding')
        assert isinstance(embedding_recommended, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
