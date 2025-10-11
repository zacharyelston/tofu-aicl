"""
v2 Configuration Module

Centralized configuration management for AICL v2 architecture.
Includes provider configs, model catalogs, and runtime settings.
"""

from .provider_loader import (
    ProviderConfig,
    ProviderConfigLoader,
    ProviderConfigValidationError,
    ProviderRuntime,
    ProviderDocker,
    ProviderEnvironment,
    ProviderCapabilities,
    ProviderModel,
    ProviderHealth
)

from .model_catalog import (
    Model,
    ModelCatalog,
    get_model_catalog
)

__all__ = [
    # Provider configs
    'ProviderConfig',
    'ProviderConfigLoader',
    'ProviderConfigValidationError',
    'ProviderRuntime',
    'ProviderDocker',
    'ProviderEnvironment',
    'ProviderCapabilities',
    'ProviderModel',
    'ProviderHealth',
    
    # Model catalog
    'Model',
    'ModelCatalog',
    'get_model_catalog'
]
