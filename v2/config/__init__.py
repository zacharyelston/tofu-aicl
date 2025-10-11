"""
v2 Configuration Module

Centralized configuration management for AICL v2 architecture.
Includes provider configs, model catalogs, and runtime settings.
"""

from .provider_loader import ProviderConfig, ProviderConfigLoader

__all__ = ['ProviderConfig', 'ProviderConfigLoader']
