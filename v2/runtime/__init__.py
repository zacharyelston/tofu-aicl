"""
v2 Runtime Module

Shared runtime utilities for AICL providers.
Eliminates gRPC boilerplate and provides standardized provider server setup.
"""

from .provider_server import ProviderServer, create_provider_server

__all__ = [
    'ProviderServer',
    'create_provider_server'
]
