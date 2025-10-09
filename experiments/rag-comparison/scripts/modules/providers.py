"""
Provider configuration and cost management for RAG experiments.

Centralizes provider-specific settings, costs, and models.
"""

from typing import Dict, Any


class ProviderConfig:
    """Configuration and cost management for LLM providers."""
    
    # Provider cost configurations (per operation)
    PROVIDER_COSTS = {
        "openai": {
            "embedding": 0.0001,
            "query": 0.002,
            "index_creation": 0.0
        },
        "azure": {
            "embedding": 0.0001,
            "query": 0.002,
            "index_creation": 0.0
        },
        "openrouter": {
            "embedding": 0.00005,
            "query": 0.001,
            "index_creation": 0.0
        }
    }
    
    # Provider model configurations
    PROVIDER_MODELS = {
        "openai": {
            "embedding": "text-embedding-ada-002",
            "chat": "gpt-3.5-turbo",
            "dimensions": 1536
        },
        "azure": {
            "embedding": "text-embedding-ada-002",
            "chat": "gpt-35-turbo",
            "dimensions": 1536
        },
        "openrouter": {
            "embedding": "text-embedding-ada-002",
            "chat": "openai/gpt-3.5-turbo",
            "dimensions": 1536
        }
    }
    
    # Context size configurations
    CONTEXT_SIZES = {
        "tiny": {"limit": 5, "description": "5 files for quick testing"},
        "small": {"limit": 10, "description": "10 files for basic comparison"},
        "medium": {"limit": 25, "description": "25 files for standard testing"},
        "large": {"limit": 50, "description": "50 files for comprehensive testing"},
        "xlarge": {"limit": 100, "description": "100 files for extensive testing"},
        "xxlarge": {"limit": 200, "description": "200 files for maximum coverage"}
    }
    
    @classmethod
    def get_provider_cost(cls, provider: str, operation: str) -> float:
        """Get cost per operation for provider."""
        return cls.PROVIDER_COSTS.get(provider, {}).get(operation, 0.001)
    
    @classmethod
    def get_embedding_model(cls, provider: str) -> str:
        """Get embedding model for provider."""
        return cls.PROVIDER_MODELS.get(provider, {}).get("embedding", "unknown")
    
    @classmethod
    def get_chat_model(cls, provider: str) -> str:
        """Get chat model for provider."""
        return cls.PROVIDER_MODELS.get(provider, {}).get("chat", "unknown")
    
    @classmethod
    def get_embedding_dimensions(cls, provider: str) -> int:
        """Get embedding dimensions for provider."""
        return cls.PROVIDER_MODELS.get(provider, {}).get("dimensions", 1536)
    
    @classmethod
    def get_context_limit(cls, context_size: str) -> int:
        """Get file limit based on context size."""
        return cls.CONTEXT_SIZES.get(context_size, {}).get("limit", 25)
    
    @classmethod
    def get_context_description(cls, context_size: str) -> str:
        """Get description for context size."""
        return cls.CONTEXT_SIZES.get(context_size, {}).get("description", "Unknown context size")
    
    @classmethod
    def validate_provider(cls, provider: str) -> bool:
        """Check if provider is supported."""
        return provider in cls.PROVIDER_COSTS
    
    @classmethod
    def validate_context_size(cls, context_size: str) -> bool:
        """Check if context size is supported."""
        return context_size in cls.CONTEXT_SIZES
    
    @classmethod
    def get_supported_providers(cls) -> list:
        """Get list of supported providers."""
        return list(cls.PROVIDER_COSTS.keys())
    
    @classmethod
    def get_supported_context_sizes(cls) -> list:
        """Get list of supported context sizes."""
        return list(cls.CONTEXT_SIZES.keys())
    
    @classmethod
    def get_provider_info(cls, provider: str) -> Dict[str, Any]:
        """Get complete provider information."""
        if not cls.validate_provider(provider):
            return {}
        
        return {
            "costs": cls.PROVIDER_COSTS[provider],
            "models": cls.PROVIDER_MODELS[provider],
            "supported": True
        }
